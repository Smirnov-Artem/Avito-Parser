import time
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import re
import random
import numpy as np
#import json
import requests
#from curl_cffi import requests
#from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_random_stealth():
    """
    Описание: возвращает рандомно сгенерированные атрибуты 
    для последующего использования в stealth driver.

    Вероятно, такая вариабельность избыточна, парсинг Avito
    работает при минимальном наборе атрибутов для драйвера.
    Тем не менее, для большей уверенности в стабильной работе
    лучше использовать как можно больше разных атрибутов.

    Returns:
        dict: Словарь из строчек.
    """

    languages = [
        ["en-US", "en"], ["en-GB", "en"], ["de-DE", "de"],
        ["fr-FR", "fr"], ["es-ES", "es"], ["ru-RU", "ru"],
        ["zh-CN", "zh"], ["ja-JP", "ja"], ["it-IT", "it"],
        ["ko-KR", "ko"], ["pt-BR", "pt"], ["nl-NL", "nl"],
        ["pl-PL", "pl"], ["sv-SE", "sv"], ["tr-TR", "tr"]
    ]

    vendors = [
        "Google Inc.", "Google LLC", "Microsoft Corporation",
        "Apple Inc.", "Mozilla Foundation", "Opera Software",
        "Samsung Electronics", "Yandex", "Baidu Inc.",
        "Huawei Technologies"
    ]

    platforms = [
        "Win32", "Win64", "MacIntel", "Linux x86_64",
        "Windows NT 10.0", "Linux armv7l", "Linux aarch64",
        "iPhone", "iPad", "Android", "FreeBSD", "NetBSD",
        "OpenBSD", "SunOS"
    ]

    webgl_vendors = [
        "Intel Inc.", "NVIDIA Corporation", "AMD Inc.",
        "ATI Technologies Inc.", "Qualcomm Inc.", "ARM Inc.",
        "Imagination Technologies", "Apple Inc.", "Broadcom Inc.",
        "Vivante Corporation"
    ]

    renderers = [
        "Intel Iris OpenGL Engine", "NVIDIA GeForce RTX 2080",
        "AMD Radeon Pro 5700 XT", "ATI Radeon HD 5450",
        "Qualcomm Adreno 640", "Intel UHD Graphics 630",
        "Apple A12X Bionic GPU", "ARM Mali-G76 MP16",
        "Vivante GC1000", "Imagination PowerVR SGX543",
        "NVIDIA Tesla P100", "NVIDIA Quadro RTX 6000"
    ]
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
    Описание: находит ссылки на искомые товары на странице,
    релевантные ссылки находятся в определенном классе страницы (items-items-kAJAg).

    Args:
        search_page_html (str): выбранная страница.

    Returns:
        возвращает лист из ссылок на релевантные товары.
    """
    soup = url
    content = soup.find("div", {"id": "app"}).find("div").find("div", {"class": "index-content-_KxNP"})
    content_with_cards = content.find_all(class_="items-items-kAJAg") if content else None
    content_with_cards = content_with_cards[0] if content_with_cards else None
    ress = []
    res = [card for card in content_with_cards] if content_with_cards else []
    # Loop through each card and extract the required data
    for card in res:
        soup = card

        try:
            # Extract product details
            product = soup.find("a", {"data-marker": "item-title"})
            product_link = "https://www.avito.ru" + product['href']
            try:
                title = product['title']
            except:
                title = ''
            description = soup.find('meta', itemprop='description')['content']
            price = float(soup.find('meta', itemprop='price')['content'])
            image_link = soup.find('li', {'data-marker': lambda x: x and x.startswith('slider-image/image')})['data-marker'].split('image-')[1]
            item_date = soup.find('p', {'data-marker': 'item-date'}).get_text()

            try:
                company_name = soup.find(class_='styles-module-root-o3j6a styles-module-size_s-xb_uK styles-module-size_s_compensated-QmHFs styles-module-size_s-__aUd styles-module-ellipsis-XeCfh styles-module-ellipsis_oneLine-_MdfX stylesMarningNormal-module-root-_BXZU stylesMarningNormal-module-paragraph-s-_lGjQ').text.strip()
            except:
                company_name = ''
            try:
                status = soup.find('span', class_='SnippetBadge-title-oSImJ').text.strip()
            except:
                status = ''
            try:
                grade = soup.find('span', {'data-marker': 'seller-rating/score'}).text.strip()
            except:
                grade = ''
            try:
                review_number = soup.find('span', {'data-marker': 'seller-rating/summary'}).text.strip()
            except:
                review_number = ''

            # Append the extracted details as a dictionary
            ress.append({
                'product_link': product_link,
                'title': title,
                'description': description,
                'price': price,
                'image_link': image_link,
                'item_date': item_date,
                'company_name': company_name,
                'status': status,
                'grade': grade,
                'review_number': review_number
            })
        except Exception as e:
            print(f"Error processing card: {e}")

    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(ress)
    return df

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
