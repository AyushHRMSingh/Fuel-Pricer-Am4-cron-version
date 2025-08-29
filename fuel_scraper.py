#!/usr/bin/env python3
"""
Simplified fuel price scraper for cron execution.
This is a one-shot script that scrapes fuel prices and sends Discord notifications if thresholds are met.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
fuel_threshold = int(os.getenv('FUEL_PRICE_THRESHOLD', 400))
co2_threshold = int(os.getenv('CO2_PRICE_THRESHOLD', 120))

if not webhook_url:
    print("Error: DISCORD_WEBHOOK_URL not found in environment variables")
    sys.exit(1)

def scrape_fuel_prices():
    """
    Scrapes fuel prices from the specified URL and sends notifications if thresholds are met.
    """
    url = "https://am4-helper.web.app/tabs/prices"
    
    # Set up headless Chrome for Linux server
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use new headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Set timezone to IST (Indian Standard Time)
    options.add_argument("--lang=en-IN")
    
    # Set timezone preference
    prefs = {
        "profile.default_content_setting_values.geolocation": 2,
        "profile.managed_default_content_settings.geolocation": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    # Set environment variable for timezone
    os.environ['TZ'] = 'Asia/Kolkata'
    
    # Try to use system Chrome first, fallback to ChromeDriverManager
    try:
        # First try with system chromedriver
        driver = webdriver.Chrome(options=options)
    except Exception as e1:
        print(f"Failed to use system Chrome, trying ChromeDriverManager: {e1}")
        try:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        except Exception as e2:
            print(f"ChromeDriverManager also failed: {e2}")
            print("Please ensure Chrome/Chromium is installed on your Linux server:")
            print("Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y chromium-browser")
            print("CentOS/RHEL: sudo yum install -y chromium")
            sys.exit(1)
    
    try:
        driver.get(url)
        
        # Set timezone to IST using JavaScript
        driver.execute_script("""
            // Override timezone to IST
            const originalDate = Date;
            Date = function(...args) {
                if (args.length === 0) {
                    const now = new originalDate();
                    // Add 5.5 hours to UTC to get IST
                    const istOffset = 5.5 * 60 * 60 * 1000;
                    return new originalDate(now.getTime() + istOffset);
                }
                return new originalDate(...args);
            };
            Date.now = function() {
                const now = originalDate.now();
                const istOffset = 5.5 * 60 * 60 * 1000;
                return now + istOffset;
            };
            Object.setPrototypeOf(Date, originalDate);
            Object.setPrototypeOf(Date.prototype, originalDate.prototype);
        """)
        
        # Wait for the "current-hour" element to be present and contain text
        wait = WebDriverWait(driver, 20)
        current_hour_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "current-hour")))
        
        # Also wait for the text to be present in the element
        wait.until(lambda driver: current_hour_element.text.strip() != "")
        
        # The data is directly within the element, separated by newlines.
        data = current_hour_element.text.split('\n')
        
        if len(data) >= 3:
            # Extract and print the text from the first three lines
            print(f"Time: {data[0]}")
            print(f"Fuel Price: {data[1]}")
            print(f"CO2 Price: {data[2]}")
            
            fuel_status = False
            co2_status = False

            if int(data[1]) < fuel_threshold:
                fuel_status = True
            if int(data[2]) < co2_threshold:
                co2_status = True

            if fuel_status or co2_status:
                # Send a notification via webhook
                message = ""
                if fuel_status:
                    message += f"Fuel price is low: {data[1]}\n"
                if co2_status:
                    message += f"CO2 price is low: {data[2]}\n" 
                payload = {"content": message}
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 204:
                    print("Notification sent successfully.")
                else:
                    print(f"Failed to send notification. Status code: {response.status_code}")
            else:
                print("Prices are above thresholds. No notification sent.")
        else:
            print("Could not find the three data elements.")
            # For debugging, print the whole current-hour element's text
            print("Content of current-hour element:")
            print(current_hour_element.text)

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_fuel_prices()
