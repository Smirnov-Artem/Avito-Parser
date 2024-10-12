from flask import Flask, request, render_template, send_file
import csv
import os
from datetime import datetime
import dateparser
import pandas as pd
import time
import numpy as np
import json
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

app = Flask(__name__)

# Setup Selenium WebDriver with stealth
def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    stealth(driver,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    
    return driver

# Route to home page
@app.route('/')
def index():
    return render_template('index.html')

# Scraper route
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']  # URL provided by user in form
    driver = init_driver()

    try:
        driver.get(url)
        time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        title = soup.title.string if soup.title else "No Title"
        
        # Example scraping logic, you can extend it
        headings = [h1.get_text() for h1 in soup.find_all('h1')]
        
        driver.quit()

        # Save the results to a CSV file
        output_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
        output_file = os.path.join(output_dir, 'scraped_data.csv')  # Save CSV to this directory
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Headings'])
            writer.writerow([title, ", ".join(headings)])
        
        return send_file(output_file, as_attachment=True)
    
    except Exception as e:
        driver.quit()
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
