from flask import Flask, render_template
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def index():
    # Пример использования chromedriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запускаем в безголовом режиме
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://www.example.com')
    title = driver.title
    driver.quit()

    return render_template('index.html', title=title)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
