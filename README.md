# Notion Trading Journal
A python script to automatically journal nse stock trades from Interactive Brokers trading account

## Features:
- Journal provides insights like Stock type (largecap/smallcap....etc.), Sector, Industry for a given stock ticker
- Auto update latest price and percentage change for ongoing trades
- Display current loss/gain and realised loss/gain for a particular trade
- Manage partial buy and sell trades edge cases as well

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
A [cron job](https://crontab.guru/#*/15_9-15_*_*_1-5) running At every 15th minute past every hour from 9 through 15 on every day-of-week from Monday through Friday, as Indian Markets are open on weekdays only - thus why waste system resources.