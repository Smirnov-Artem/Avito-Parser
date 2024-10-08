from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

# Настройки для chromedriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Работа в headless режиме
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error_message = None

    if request.method == 'POST':
        # Получаем URL от пользователя
        url = request.form.get('url')

        # Проверяем, что URL начинается с http:// или https://
        if url and (url.startswith("http://") or url.startswith("https://")):
            # Путь к chromedriver
            chrome_service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))

            # Запускаем chromedriver и парсим контент страницы
            try:
                with webdriver.Chrome(service=chrome_service, options=chrome_options) as driver:
                    driver.get(url)
                    title = driver.title
                    
                    # Находим первый параграф на странице
                    try:
                        element = driver.find_element(By.TAG_NAME, 'p')
                        paragraph = element.text
                    except:
                        paragraph = "No paragraph found on this page."

                    result = {
                        'url': url,
                        'title': title,
                        'paragraph': paragraph
                    }
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Please enter a valid URL starting with http:// or https://."

    return render_template('index.html', result=result, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
