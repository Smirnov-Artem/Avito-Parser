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
    Описание: прокручивает активную страницу вниз.

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): драйвер.
        num_scrolls (int): сколько раз нужно выполнить прокрутку страницы вниз.

    Returns:
        selenium.webdriver.chrome.webdriver.WebDriver: сгенерированный драйвер.
    """

    for _ in range(num_scrolls):
        driver.execute_script('window.scrollBy(0, 500)')
        time.sleep(0.1)

def get_searchpage_cards(q, driver, page_url, i, all_cards=[]):
    """
    Описание: рекурсивно возвращает лист из доступных ссылок на товары, включая нерелевантые (предложенные самим сайтом)
    на активной странице, пока есть следующая страница.

    Args:
        q (str): запрос вида "iphone+15".
        driver (selenium.webdriver.chrome.webdriver.WebDriver): драйвер.
        page_url (str): адрес страницы для поиска товаров.
        i (int): номер страницы.
        all_cards (list): список из URLs.

    Returns:
        all_cards (list): список из URLs.
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

def fetch_urls(query):
    """
    Fetches product data for a given query from Avito.

    Args:
        query (str): The query string (e.g., 'iphone+15+pro').

    Returns:
        pd.DataFrame: DataFrame of the results.
    """
    base_url = f'https://www.avito.ru/all?q={query}'
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
            try:
                price = float(item.find('meta', itemprop='price')['content'])
            except:
                price = ''
            try:
                description = item.find('meta', itemprop='description')['content']
            except:
                description = ''
            item_url = 'https://www.avito.ru' + item.find('a')['href']
            item_date = item.find('p', {'data-marker': 'item-date'}).get_text()
            #image_link = item.find('li', {'data-marker': lambda x: x and x.startswith('slider-image/image')})['data-marker'].split('image-')[1] else 'N/A'
            
            results.append({
                'title': title,
                'price': price,
                'description': description,
                'item_url': item_url,
                'item_date': item_date,
                #'image_link': image_link
            })

        # Debugging: Check the results collected
        print(f"Results for query '{query}': {results}")

        # Convert the results to a DataFrame
        df = pd.DataFrame(results)
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL for query '{query}': {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
