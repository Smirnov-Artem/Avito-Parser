import time
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import re
import random

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

def fetch_urls(query):
    """
    Возвращает ссылки на товары по запросу.
    """
    driver = init_webdriver()
    url_search = "https://www.avito.ru/all?cd=1&q=" + query
    search_page_html_all = get_searchpage_cards(query, driver, url_search, 1)
    infos = []
    for html in search_page_html_all:
        card_urls_and_info = extract_card_urls(html)
        infos.append(card_urls_and_info)
    driver.quit()
    return pd.concat(infos)
