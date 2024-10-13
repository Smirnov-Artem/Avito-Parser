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
        output_file = 'scraped_data.csv'
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

# def generate_random_stealth():
#     """
#     Returns randomly generated attributes for the stealth driver.
#     """
    
#     user_agents = [
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
#         "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:89.0) Gecko/20100101 Firefox/89.0",
#         "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
#     ]

#     languages = [
#         ["en-US", "en"], ["en-GB", "en"], ["de-DE", "de"],
#         ["fr-FR", "fr"], ["es-ES", "es"], ["ru-RU", "ru"],
#         ["zh-CN", "zh"], ["ja-JP", "ja"], ["it-IT", "it"],
#         ["ko-KR", "ko"], ["pt-BR", "pt"], ["nl-NL", "nl"],
#         ["pl-PL", "pl"], ["sv-SE", "sv"], ["tr-TR", "tr"]
#     ]

#     vendors = [
#         "Google Inc.", "Google LLC", "Microsoft Corporation",
#         "Apple Inc.", "Mozilla Foundation", "Opera Software",
#         "Samsung Electronics", "Yandex", "Baidu Inc.",
#         "Huawei Technologies"
#     ]

#     platforms = [
#         "Win32", "Win64", "MacIntel", "Linux x86_64",
#         "Windows NT 10.0", "Linux armv7l", "Linux aarch64",
#         "iPhone", "iPad", "Android", "FreeBSD", "NetBSD",
#         "OpenBSD", "SunOS"
#     ]

#     webgl_vendors = [
#         "Intel Inc.", "NVIDIA Corporation", "AMD Inc.",
#         "ATI Technologies Inc.", "Qualcomm Inc.", "ARM Inc.",
#         "Imagination Technologies", "Apple Inc.", "Broadcom Inc.",
#         "Vivante Corporation"
#     ]

#     renderers = [
#         "Intel Iris OpenGL Engine", "NVIDIA GeForce RTX 2080",
#         "AMD Radeon Pro 5700 XT", "ATI Radeon HD 5450",
#         "Qualcomm Adreno 640", "Intel UHD Graphics 630",
#         "Apple A12X Bionic GPU", "ARM Mali-G76 MP16",
#         "Vivante GC1000", "Imagination PowerVR SGX543",
#         "NVIDIA Tesla P100", "NVIDIA Quadro RTX 6000"
#     ]

#     return {
#         "user_agent": random.choice(user_agents),
#         "languages": random.choice(languages),
#         "vendor": random.choice(vendors),
#         "platform": random.choice(platforms),
#         "webgl_vendor": random.choice(webgl_vendors),
#         "renderer": random.choice(renderers),
#         "fix_hairline": True
#     }

# def init_driver():
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--headless")  # Run in headless mode
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")

#     stealth_attrs = generate_random_stealth()
    
#     # Add randomized user agent
#     chrome_options.add_argument(f"user-agent={stealth_attrs['user_agent']}")
    
#     driver = webdriver.Chrome(options=chrome_options)
    
#     stealth(driver,
#             user_agent=stealth_attrs["user_agent"],
#             languages=stealth_attrs["languages"],
#             vendor=stealth_attrs["vendor"],
#             platform=stealth_attrs["platform"],
#             webgl_vendor=stealth_attrs["webgl_vendor"],
#             renderer=stealth_attrs["renderer"],
#             fix_hairline=True)
    
#     driver.set_window_size(1920, 1080)
#     return driver

# def extract_card_urls(url):
#     """
#     Описание: находит ссылки на искомые товары на странице,
#     релевантные ссылки находятся в определенном классе страницы (items-items-kAJAg).

#     Args:
#         search_page_html (str): выбранная страница.

#     Returns:
#         возвращает лист из ссылок на релевантные товары.
#     """
#     soup = url
#     content = soup.find("div", {"id": "app"}).find("div").find("div", {"class": "index-content-_KxNP"})
#     content_with_cards = content.find_all(class_="items-items-kAJAg") if content else None
#     content_with_cards = content_with_cards[0] if content_with_cards else None
#     ress = []
#     res = [card for card in content_with_cards] if content_with_cards else []
#     # Loop through each card and extract the required data
#     for card in res:
#         soup = card

#         try:
#             # Extract product details
#             product = soup.find("a", {"data-marker": "item-title"})
#             product_link = "https://www.avito.ru" + product['href']
#             try:
#                 title = product['title']
#             except:
#                 title = ''
#             description = soup.find('meta', itemprop='description')['content']
#             price = float(soup.find('meta', itemprop='price')['content'])
#             image_link = soup.find('li', {'data-marker': lambda x: x and x.startswith('slider-image/image')})['data-marker'].split('image-')[1]
#             item_date = soup.find('p', {'data-marker': 'item-date'}).get_text()

#             try:
#                 company_name = soup.find(class_='styles-module-root-o3j6a styles-module-size_s-xb_uK styles-module-size_s_compensated-QmHFs styles-module-size_s-__aUd styles-module-ellipsis-XeCfh styles-module-ellipsis_oneLine-_MdfX stylesMarningNormal-module-root-_BXZU stylesMarningNormal-module-paragraph-s-_lGjQ').text.strip()
#             except:
#                 company_name = ''
#             try:
#                 status = soup.find('span', class_='SnippetBadge-title-oSImJ').text.strip()
#             except:
#                 status = ''
#             try:
#                 grade = soup.find('span', {'data-marker': 'seller-rating/score'}).text.strip()
#             except:
#                 grade = ''
#             try:
#                 review_number = soup.find('span', {'data-marker': 'seller-rating/summary'}).text.strip()
#             except:
#                 review_number = ''

#             # Append the extracted details as a dictionary
#             ress.append({
#                 'product_link': product_link,
#                 'title': title,
#                 'description': description,
#                 'price': price,
#                 'image_link': image_link,
#                 'item_date': item_date,
#                 'company_name': company_name,
#                 'status': status,
#                 'grade': grade,
#                 'review_number': review_number
#             })
#         except Exception as e:
#             print(f"Error processing card: {e}")

#     # Convert the list of dictionaries into a Pandas DataFrame
#     df = pd.DataFrame(ress)
#     return df
# # Route to home page
# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# @app.route('/')
# def index():
#     user_ip = request.remote_addr  # Capture user's IP address
#     return render_template('index.html', ip=user_ip)  # Pass it to the template

# # Scraper route
# @app.route('/scrape', methods=['POST'])
# # def scrape():
# #     url = request.form['url']  # URL provided by user in form
# #     driver = init_driver()

# #     try:
# #         driver.get(url)
# #         time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

# #         soup = BeautifulSoup(driver.page_source, 'html.parser')
# #         title = soup.title.string if soup.title else "No Title"
        
# #         # Example scraping logic, you can extend it
# #         headings = [h1.get_text() for h1 in soup.find_all('h1')]
        
# #         driver.quit()

# #         # Save the results to a CSV file
# #         output_file = 'scraped_data.csv'
# #         with open(output_file, 'w', newline='') as csvfile:
# #             writer = csv.writer(csvfile)
# #             writer.writerow(['Title', 'Headings'])
# #             writer.writerow([title, ", ".join(headings)])
        
# #         return send_file(output_file, as_attachment=True)
    
# #     except Exception as e:
# #         driver.quit()
# #         return str(e)


# def scrape():
#     url = request.form['url']  # URL provided by user in form
#     driver = init_driver()
#     try:
#         driver.get(url)
#         time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior

#         # Capture the page source (HTML content)
#         page_source = driver.page_source

#         # Parse HTML with BeautifulSoup
#         soup = BeautifulSoup(page_source, 'html.parser')
#         df = extract_card_urls(soup)  # Assume this returns a DataFrame
#         title = soup.title.string if soup.title else "No Title"

#         # Save the DataFrame to a CSV file
#         output_file = 'scraped_data.csv'
#         df.to_csv(output_file, index=False)

#         driver.quit()

#         return send_file(output_file, as_attachment=True)
    
#     except Exception as e:
#         driver.quit()
#         return str(e)

# if __name__ == '__main__':
#     app.run(debug=True)
