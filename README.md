# Notion Trading Journal
A python script to automatically journal NSE stock trades using Interactive Brokers trading account email notifications

## Features: 
- Journal provides insights like Stock type (largecap/midcap....etc.), Sector, Industry for a given stock ticker
- Auto update latest price and percentage change for ongoing trades
- Display current loss/gain and realised loss/gain for a particular trade
- Provides holding time period for each trade in Days
- Classify trades to different categories based on percentage of loss/gain and holding period

## Requirements:

```bash
pip3 install requests nsetools yfinance
```
## API's Usage:
[Notion Official API](https://developers.notion.com/reference/intro)

## Script Automation:
```
*/15 9-15 * * 1-5
```
A [cron job](https://crontab.guru/#*/15_9-15_*_*_1-5) running At every 15th minute past every hour from 9 through 15 on every day-of-week from Monday through Friday, as Indian Markets are open on only on weekdays.
