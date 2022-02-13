# Notion Trading Journal
A python script to automatically journal NSE stock trades by leveraging Interactive Broker email notifications for the buy/sell trades.

## Features: 
- Journal provides insights like Stock type (largecap/midcap....etc.), Sector, Industry for a given stock ticker
- Auto update latest price and percentage change for ongoing trades
- Display current loss/gain and realised loss/gain for a particular trade
- Provides holding time period for each trade in Days
- Classify trades to different categories based on percentage of loss/gain and holding period
- Manage edge cases like buy/sell trades notifications (partial trades)

## Requirements:

```bash
pip3 install requests nsetools yfinance
```
## API's Usage:
[Notion Official API](https://developers.notion.com/reference/intro)

## Script Automation:
```
35 15 * * 1-5
```
A [cron job](https://crontab.guru/#35_15_*_*_1-5) running at 15:35 on every day-of-week from Monday through Friday, will gather all the buy/sell trades emails and journal them post market-closing. 

P.S. In case, you wants to keep the current price updated for the ongoing trades, just grab the relevant section from the [main.py](https://github.com/ashleymavericks/notion-trading/blob/master/main.py) and set a recurring cron job during the market hours.
