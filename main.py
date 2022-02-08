from env_vars import *
import imaplib
import email
from email.header import decode_header
import requests
from nsetools import Nse
import dateutil.parser as parser
import yfinance as yf
import csv

secret_key = NOTION_SECRET_KEY
trading_database_id = NOTION_TRADING_DB

base_db_url = "https://api.notion.com/v1/databases/"
base_pg_url = "https://api.notion.com/v1/pages/"
username = EMAIL_UN
password = EMAIL_PW

header = {"Authorization": secret_key,
          "Notion-Version": "2021-05-13", "Content-Type": "application/json"}

nse = Nse()
all_stock_codes = nse.get_stock_codes()

largecap_file = open('assets/ind_nifty100list.csv')
midcap_file = open('assets/ind_niftymidcap150list.csv')
smallcap_file = open('assets/ind_niftysmallcap250list.csv')
microcap_file = open('assets/ind_niftymicrocap250_list.csv')

def stock_type_classification(stock_type):
    csvreader = csv.reader(stock_type)
    rows = []
    stock_list = []
    for row in csvreader:
        rows.append(row)   
    for column in rows:
        stock_list.append(column[2])
    stock_type.close()
    return stock_list

LargeCap = stock_type_classification(largecap_file)
MidCap = stock_type_classification(midcap_file)
SmallCap = stock_type_classification(smallcap_file)
MicroCap = stock_type_classification(microcap_file)

def stock_fundamentals(ticker):
    modified_ticker = ticker + '.NS'
    quote = yf.Ticker(modified_ticker)
    ticker_info = quote.info
    industry = ticker_info['industry']
    for y in LargeCap,MidCap,SmallCap,MicroCap:
        if ticker in y:
            for key,val in globals().items():
                if y == val:
                    return [key, industry]

def trade_quality(page_id):
    page_db = requests.get(base_pg_url + page_id, headers=header)
    page_db_json = page_db.json()
    buy_price = float(page_db_json['properties']['Buying Price']['number'])
    sell_price = float(page_db_json['properties']['Selling Price']['number'])
    holding_period = page_db_json['properties']['HODL Period']['formula']['number']
    loss_gain_percent = ((sell_price - buy_price) / buy_price)*100

    if loss_gain_percent > 9 and holding_period <= 10:
        quality = 'Great'
    elif loss_gain_percent >= 0.5:
        quality = 'Good'
    elif loss_gain_percent >= -7:
        quality = 'Loss'
    else:
        quality = 'Worst'
    return quality    

response_stocks_db = requests.post(
    base_db_url + trading_database_id + "/query", headers=header)

existing_trades = {}

for page in response_stocks_db.json()["results"]:
    page_id = page["id"]
    props = page['properties']
    ticker_check = props['Ticker']['rich_text']
    if ticker_check:
        ticker = props['Ticker']['rich_text'][0]['text']['content']
        checkbox_state = props['Trade Status']['checkbox']
        if checkbox_state is False:
            existing_trades[ticker] = page_id
            quote = nse.get_quote(ticker)
            current_price = quote['lastPrice']
            percent_change = float(quote['pChange'])
            price_payload = {"properties":{
                "Current Price": {"number": current_price},
                "1D": {"number": percent_change}
                }
            }
            update_trade = requests.patch(
                        base_pg_url + page_id, headers=header, json=price_payload)

# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(username, password)
status, messages = imap.select("INBOX")

# number of top emails to fetch
N = 20
messages = int(messages[0])

for i in range(messages, messages-N, -1):
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])

            # decode the email date
            date, encoding = decode_header(msg["Date"])[0]
            if isinstance(date, bytes):
                date = date.decode(encoding)
            date = parser.parse(date)
            date_iso = date.isoformat()
            date_modified = date_iso[0:10]

            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)

            if subject.__contains__('BOUGHT'):
                res = subject.split()
                units = int(res[1])
                ticker = res[2]
                buying_price = float(res[5])

                # fuzzy match on dict keys to get the accurate ticker
                company_quote = [
                    (key, value) for key, value in all_stock_codes.items() if ticker in key]
                company_ticker = company_quote[0][0]
                company_name = company_quote[0][1]

                # removing "Limited" | "Ltd" from company name
                company_name = company_name.replace("Limited", "")
                company_name = company_name.replace("Ltd", "")

                ticker_info = stock_fundamentals(company_ticker)
                stock_type = ticker_info[0]
                industry = ticker_info[1]

                response_db = requests.post(
                    base_db_url + trading_database_id + "/query", headers=header)

                if company_ticker not in existing_trades:
                    add_payload = {
                        "parent": {
                            "database_id": NOTION_TRADING_DB
                        },
                        "properties": {
                            "Trade Status": {"checkbox": False},
                            "Type": {
                                "select": {"name": stock_type}
                            },
                            "Industry": {
                                "select": {"name": industry}
                            },
                            "Buying Price": {"number": buying_price},
                            "Units": {"number": units},
                            "Bought On": {
                                "date": {"start": date_modified}
                            },
                            "Ticker": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": company_ticker
                                        }
                                    }
                                ]
                            },
                            "Name": {
                                "title": [
                                    {
                                        "text": {
                                            "content": company_name
                                        }
                                    }
                                ]
                            }
                        }
                    }
                    add_trade = requests.post(
                        base_pg_url, headers=header, json=add_payload)

            if subject.__contains__('SOLD'):
                res = subject.split()
                ticker = res[2]
                units_sold = int(res[1])
                selling_price = float(res[5])

                company_quote = [
                    (key, value) for key, value in all_stock_codes.items() if ticker in key]
                company_ticker = company_quote[0][0]

                if company_ticker in existing_trades:
                    page_id = existing_trades[company_ticker]
                    update_payload = {
                        "properties": {
                            "Trade Status": {"checkbox": True},
                            "Selling Price": {"number": selling_price},
                            "Sold On": {
                                "date": {"start": date_modified}
                            }
                        }
                    }
                    update_trade = requests.patch(
                        base_pg_url + page_id, headers=header, json=update_payload)
                    
                    quality = trade_quality(page_id)
                    update_quality_payload = {
                        "properties": {
                            "Quality": {
                                "select": {"name": quality}
                            }
                        }
                    }
                    add_quality = requests.patch(
                        base_pg_url + page_id, headers=header, json=update_quality_payload)

# close the connection and logout
imap.close()
imap.logout()