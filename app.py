# from flask import Flask, request, render_template, send_file
# import csv
# import os
# from datetime import datetime
# import dateparser
# import pandas as pd
# import time
# import numpy as np
# import json
# from selenium import webdriver
# from selenium_stealth import stealth
# from bs4 import BeautifulSoup
# import random
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import re

# app = Flask(__name__)

# # Setup Selenium WebDriver with stealth
# def init_driver():
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--headless")  # Run in headless mode
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
    
#     driver = webdriver.Chrome(options=chrome_options)
#     stealth(driver,
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True)
    
#     return driver

# # Route to home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Scraper route
# @app.route('/scrape', methods=['POST'])
# def scrape():
#     url = request.form['url']  # URL provided by user in form
#     driver = init_driver()

#     try:
#         driver.get(url)
#         time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         title = soup.title.string if soup.title else "No Title"
        
#         # Example scraping logic, you can extend it
#         headings = [h1.get_text() for h1 in soup.find_all('h1')]
        
#         driver.quit()

#         # Save the results to a CSV file
#         output_file = 'scraped_data.csv'
#         with open(output_file, 'w', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow(['Title', 'Headings'])
#             writer.writerow([title, ", ".join(headings)])
        
#         return send_file(output_file, as_attachment=True)
    
#     except Exception as e:
#         driver.quit()
#         return str(e)

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, render_template, send_file
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from avito_parser import *
import os
from datetime import datetime
import dateparser
import pandas as pd

app = Flask(__name__)

def write_to_csv(all_urls, filename="output.csv"):
    """
    Write the result to a CSV file.
    """
    all_urls.to_csv(filename, index=False, encoding='utf-8', columns=all_urls.columns)

def process_queries(queries):
    """
    Process the provided queries to return relevant products.
    """
    queries = [query.replace(" ", "+") for query in queries]
    all_urls = []
    with ThreadPoolExecutor(max_workers=len(queries)) as executor:
        future_to_query = {executor.submit(fetch_urls, query): query for query in queries}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                data = future.result()
                all_urls.append(data)
            except Exception as exc:
                print(f"{query} generated an exception: {exc}")
    all_urls = pd.concat(all_urls) if all_urls else pd.DataFrame()  # Ensure it's not empty
    return all_urls

def filter_descriptions_perfumes(df, units=['ml', 'мл'], min_value=11):
    """
    Filters perfumes based on quantity in ml.
    """
    unit_pattern = '|'.join(units)
    pattern = fr'\b(\d+(\.\d+)?)\s*({unit_pattern})\b'
    
    def extract_quantity(text):
        match = re.search(pattern, text)
        if match:
            quantity = float(match.group(1))
            if quantity > min_value:
                return quantity
        return None

    quantity_description = df['description'].apply(extract_quantity)
    quantity_title = df['title'].apply(extract_quantity)
    combined_quantities = quantity_description.combine_first(quantity_title)
    mask = combined_quantities.notna()
    new_df = df[mask].copy()
    new_df['quantity_ml'] = combined_quantities[mask]
    new_df['price_per_ml'] = round(new_df['price'] / new_df['quantity_ml'], 2)
    new_df = new_df.sort_values(by='price_per_ml', ascending=False, na_position='first')
    return new_df

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles search queries and CSV download.
    """
    if request.method == 'POST':
        queries = request.form.get('queries').split(',')
        current_time = datetime.now()
        q_names = '_'.join([query.replace(' ', '+') for query in queries])
        output_filename = q_names + str(current_time).replace(' ', '_')[:-7] + ".csv"

        all_urls = process_queries(queries)
        
        if all_urls.empty:
            return "No data scraped. Please check the query or website structure."

        all_urls['timestamp'] = all_urls['item_date'].apply(lambda x: dateparser.parse(x))

        perfumes = False
        all_urls = all_urls.drop_duplicates()
        if perfumes:
            all_urls = filter_descriptions_perfumes(all_urls)

        write_to_csv(all_urls, filename=output_filename)
        return send_file(output_filename, as_attachment=True, download_name=output_filename)

    return render_template('index.html')

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8080))
#     app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    app.run(debug=True)
