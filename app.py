from flask import Flask, request, render_template, send_file
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from avito_parser import *
import os
from datetime import datetime
import dateparser

app = Flask(__name__)

def write_to_csv(all_urls, filename="output.csv"):
    """
    Описание: записывает результат в CSV-файл.

    Args:
        all_urls (pd.DataFrame): DataFrame со ссылками на товары.
        filename (str): название файла.
    """

    all_urls.to_csv(filename, index=False, encoding='utf-8', columns=all_urls.columns)

def process_queries(queries):
    """
    Описание: возвращает все искомые товары.

    Args:
        queries (list): запрос(ы) вида ["iphone 15 pro", "ноутбук lenovo"].

    Returns:
        list(set(all_urls)): список всех релевантных найденных товаров по запросу / запросам.
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
    all_urls = pd.concat(all_urls)
    return all_urls

def filter_descriptions_perfumes(df,units=['ml', 'мл', 'ML', 'МЛ', 'Ml', 'Мл', 'миллилитров', 'Миллилитров'], min_value=11):
    """
    Filters rows in the DataFrame where the 'description' or 'title' columns contain
    a number greater than a specified threshold followed by specific units and adds
    a column with the quantity in milliliters.

    Parameters:
    df (pd.DataFrame): The original DataFrame with 'description' and 'title' columns.
    units (list): A list of units to search for (e.g., ['ml', 'мл']).
    min_value (int or float): The minimum value for filtering (default is 10).

    Returns:
    pd.DataFrame: A new DataFrame with rows that match the condition and a column
                  containing the milliliter quantity.
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
    new_df['price_per_ml'] = round(new_df['price'] / new_df['quantity_ml'],2)
    new_df = new_df.sort_values(by='price_per_ml', ascending=False, na_position='first')
    return new_df

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Описание: обработка запроса / запросов в веб-приложении Flask.

    Returns:
        send_file(output_filename, as_attachment=True, download_name=output_filename) : отправка файла пользователю для скачивания.
        render_template('index.html') : если метод запроса не 'POST', рендерим и отображаем HTML-шаблон 'index.html'.
    """
    
    if request.method == 'POST':
        queries = request.form.get('queries').split(',')
        current_time = datetime.now()
        q_names = '_'.join([query.replace(' ', '+') for query in queries])
        output_filename = q_names + str(current_time).replace(' ', '_')[:-7] + ".csv"
        all_urls = process_queries(queries)
        all_urls['timestamp'] = all_urls['item_date'].apply(lambda x: dateparser.parse(x))
        perfumes = True
        all_urls = all_urls.drop_duplicates()
        if perfumes == True:
            all_urls = filter_descriptions_perfumes(all_urls)
        write_to_csv(all_urls, filename=output_filename)
        return send_file(output_filename, as_attachment=True, download_name=output_filename)

    return render_template('index.html')

# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
