# Fuel Scraper - Cron Version

A simplified, one-shot fuel price scraper designed to run via cron jobs.

## Overview

This script scrapes fuel prices from AM4 Helper and sends Discord notifications when prices fall below configured thresholds. Unlike the main project, this version is designed as a simple one-shot script without any scheduling services or signal handlers.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord webhook URL and thresholds
   ```

3. **Test the script:**
   ```bash
   python fuel_scraper.py
   ```

## Cron Configuration

To run the scraper every 30 minutes, add this to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path as needed):
3,33 * * * * cd /path/to/fuel-pricer-cron && python fuel_scraper.py >> scraper.log 2>&1
```

This will run the scraper at 3 and 33 minutes past every hour, logging output to `scraper.log`.

## Configuration

- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL (required)
- `FUEL_PRICE_THRESHOLD`: Fuel price threshold (default: 400)
- `CO2_PRICE_THRESHOLD`: CO2 price threshold (default: 120)

## Dependencies

- `selenium`: Web scraping
- `webdriver-manager`: Chrome driver management
- `requests`: HTTP requests for Discord webhooks
- `python-dotenv`: Environment variable management
