import time
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import re
import random
import requests

def generate_random_stealth():
    """
    Возвращает случайные атрибуты для stealth браузера.
    """
    languages = [
        ["en-US", "en"], ["ru-RU", "ru"], ["fr-FR", "fr"]
    ]

    vendors = ["Google Inc.", "Microsoft Corporation", "Mozilla Foundation"]

    platforms = ["Win32", "Win64", "MacIntel", "Linux x86_64"]

    webgl_vendors = ["Intel Inc.", "NVIDIA Corporation", "AMD Inc."]

    renderers = ["Intel Iris OpenGL Engine", "NVIDIA GeForce RTX 2080", "AMD Radeon Pro 5700 XT"]

    return {
        "languages": random.choice(languages),
        "vendor": random.choice(vendors),
        "platform": random.choice(platforms),
        "webgl_vendor": random.choice(webgl_vendors),
        "renderer": random.choice(renderers),
        "fix_hairline": True
    }

def init_webdriver(proxy=None):
    """
    Инициализация драйвера.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    driver = webdriver.Chrome(options=chrome_options)
    stealth_attrs = generate_random_stealth()
    stealth(driver,
            languages=stealth_attrs["languages"],
            vendor=stealth_attrs["vendor"],
            platform=stealth_attrs["platform"],
            webgl_vendor=stealth_attrs["webgl_vendor"],
            renderer=stealth_attrs["renderer"],
            fix_hairline=True)
    driver.set_window_size(1920, 1080)
    return driver

def scrolldown(driver, num_scrolls):
    """
    Прокрутка страницы вниз.
    """
    for _ in range(num_scrolls):
        driver.execute_script('window.scrollBy(0, 500)')
        time.sleep(0.1)

def get_searchpage_cards(q, driver, page_url, i, all_cards=[]):
    """
    Рекурсивный поиск товаров на страницах.
    """
    driver.get(page_url)
    scrolldown(driver, 20)
    search_page_html = BeautifulSoup(driver.page_source, "html.parser")
    all_cards.append(search_page_html)
    next_page_tag = None
    aria_label = search_page_html.find_all('a')
    for tag in aria_label:
        if 'aria-label' in tag.attrs and tag['aria-label'] == "Следующая страница":
            next_page_tag = tag
            break
    if next_page_tag:
        next_page_url = f"https://www.avito.ru/all?cd=1&p={i+1}&q=" + q
        return get_searchpage_cards(q, driver, next_page_url, i + 1, all_cards)
    return all_cards

def extract_card_urls(url):
    """
    Извлечение URL товаров на странице.
    """
    soup = url
    content = soup.find("div", {"id": "app"}).find("div").find("div", {"class": "index-content-_KxNP"})
    content_with_cards = content.find_all(class_="items-items-kAJAg") if content else None
    ress = []
    if content_with_cards:
        res = [card for card in content_with_cards[0]]
        for card in res:
            try:
                product = card.find("a", {"data-marker": "item-title"})
                product_link = "https://www.avito.ru" + product['href']
                title = product.get('title', '')
                description = card.find('meta', itemprop='description')['content']
                price = float(card.find('meta', itemprop='price')['content'])
                item_date = card.find('p', {'data-marker': 'item-date'}).text

                ress.append({
                    'product_link': product_link,
                    'title': title,
                    'description': description,
                    'price': price,
                    'item_date': item_date
                })
            except Exception as e:
                print(f"Error processing card: {e}")

    return pd.DataFrame(ress)

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_urls(query):
    """
    Fetches product data for a given query from Avito.

    Args:
        query (str): The query string (e.g., 'iphone+15+pro').

    Returns:
        pd.DataFrame: DataFrame of the results.
    """
    base_url = f'https://www.avito.ru/rossiya?q={query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        # Debugging: Check if we got a response and its status
        print(f"Response status code for query '{query}': {response.status_code}")
        print(f"URL: {response.url}")

        # Parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Debugging: Check the page title or structure to verify correct page
        print(f"Page title: {soup.title.string}")

        # Find listings: Adjust the selector based on Avito's structure
        items = soup.find_all('div', {'data-marker': 'item'})

        # Debugging: Check how many items were found
        print(f"Number of items found for query '{query}': {len(items)}")

        # Collect item data
        results = []
        for item in items:
            title = item.find('h3').get_text(strip=True)
            price = item.find('span', {'data-marker': 'price'}).get_text(strip=True) if item.find('span', {'data-marker': 'price'}) else 'N/A'
            item_url = 'https://www.avito.ru' + item.find('a')['href']
            item_date = item.find('div', {'data-marker': 'item-date'}).get_text(strip=True) if item.find('div', {'data-marker': 'item-date'}) else 'N/A'

            results.append({
                'title': title,
                'price': price,
                'item_url': item_url,
                'item_date': item_date
            })

        # Debugging: Check the results collected
        print(f"Results for query '{query}': {results}")

        # Convert the results to a DataFrame
        df = pd.DataFrame(results)
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL for query '{query}': {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
