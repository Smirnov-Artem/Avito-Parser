from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

# Настройки для chromedriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

@app.route('/')
def index():
    # Путь к chromedriver
    chrome_service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver"))

    # Запускаем chromedriver
    with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
        driver.get('https://www.python.org/')
        title = driver.title
        element = driver.find_element(By.CLASS_NAME, 'introduction')
        intro_text = element.text
        # Возвращаем результат работы браузера
        return render_template('index.html', title=title, intro=intro_text)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
