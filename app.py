from flask import Flask, render_template, request, redirect, url_for, stream_with_context, Response, send_file
from concurrent.futures import ThreadPoolExecutor, as_completed
from avito_parser import *
from modeling_and_plots import *
from cyrillization import *
import os
from datetime import datetime
import dateparser
from unidecode import unidecode
import pgeocode

app = Flask(__name__)

###############################################################
# Для виджетов визуальной части приложения
###############################################################
plotting_status_map = ''
plotting_status = ''
modeling_status = ''
data_ready = False
results_data = None
plots = None
geomaps = None
output_filename = None
all_urls = None
reset_button = False
###############################################################

def write_to_csv(all_urls, filename="output.csv"):
    """
    Описание: записывает результат в CSV-файл.

    Args:
        all_urls (pd.DataFrame): DataFrame со ссылками на товары.
        filename (str): название файла.
    """

    all_urls.to_csv(filename, index=False, encoding='utf-8', columns=all_urls.columns)
    
def process_queries(queries, region, reset_button):
    """
    Описание: возвращает все искомые товары.

    Args:
        queries (list): запрос(ы) вида ["iphone 15 pro", "ноутбук lenovo"].

    Returns:
        pd.DataFrame: DataFrame всех релевантных найденных товаров по запросу / запросам.
    """

    queries = [query.replace(" ", "+") for query in queries]
    all_urls = []

    with ThreadPoolExecutor(max_workers=len(queries)) as executor: # Одновременный поиск для нескольких запросов
        future_to_query = None
        future_to_query = {executor.submit(fetch_urls, query, region, len(queries), reset_button): query for query in queries}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            data = future.result()
            try:
                data = future.result()
                if data is not None:  # Если данные успешно выгружены
                    all_urls.append(data)
            except Exception as exc:
                print(f"{query} generated an exception: {exc}")
    
    if all_urls:  # Если даже одна URL существует
        all_urls = pd.concat(all_urls)  # Общий DataFrame
        return all_urls
    else:
        return pd.DataFrame()  # Пустой DataFrame если ничего не выгружено

def render_warning(message):

    """ Отдельная функция для возврата шаблона страницы с нужным предупреждением. """
    
    return render_template(
        'warning.html', 
        modeling_status=modeling_status, 
        plotting_status_map=plotting_status_map,
        plotting_status=plotting_status, 
        data_ready=data_ready, 
        warning=message
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    global plotting_status, plotting_status_map, modeling_status, data_ready, output_filename, all_urls, queries, queries_for_html
    if request.method == 'POST':
        plotting_status_map = '⏳'
        plotting_status = '⏳'
        modeling_status = '⏳'
        queries = request.form.get('queries').split(',')
        if len(queries) >= 2:
            queries_for_html = ', '.join(queries[:-1]) + ' и ' + queries[-1]
        else:
            queries_for_html = queries[0]
        region = request.form.get('region')
        if region == "Все регионы":
            region = "all"
        elif region == "Другой город":
            region = request.form.get('city')
        region = re.sub(r'ий\b', 'iy', region)
        region = unidecode(region.lower()).replace(" ", "_")
        current_time = datetime.now()
        q_names = '_'.join([query.replace(' ', '+') for query in queries])

        #output_filename = os.path.join(q_names + "_" + str(current_time).replace(' ', '_')[:-7] + ".csv")
        output_filename = os.path.join(os.getcwd(), f"{q_names}_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.csv")

        all_urls = process_queries(queries, region, reset_button)

        if not all_urls.empty:
            data_ready = True
            try:
                all_urls['timestamp'] = all_urls['item_date'].apply(lambda x: dateparser.parse(x).strftime('%Y-%m-%d %H:%M:%S'))
                all_urls['timestamp'] = pd.to_datetime(all_urls['timestamp'])
                all_urls['timestamp_seconds'] = all_urls['timestamp'].astype(np.int64) // 10**9
                current_time = pd.Timestamp.now().floor('H')
                current_time_seconds = int(current_time.timestamp())
                all_urls['time_duration'] = current_time_seconds - all_urls['timestamp_seconds']
            except:
                pass

            all_urls = all_urls.drop_duplicates(subset=['product_link'])
            all_urls['rus_location'] = all_urls['location'].apply(convert_to_cyrillic)

            nomi = pgeocode.Nominatim('ru')
            yanao_cities = ["Новый Уренгой", "Ноябрьск", "Салехард", "Надым", "Муравленко", "Лабытнанги", "Губкинский",
                "Тарко-Сале", "Пангоды", "Уренгой", "Пурпе", "Тазовский", "Яр-Сале", "Харп"]
            hmao_cities = [
                "Сургут", "Нижневартовск", "Нефтеюганск", "Ханты-Мансийск", "Когалым", "Нягань", "Мегион", "Лангепас",
                "Радужный", "Пыть-Ях", "Урай", "Лянтор", "Югорск", "Советский", "Пойковский", "Фёдоровский",
                "Белоярский", "Излучинск", "Покачи", "Белый Яр", "Нижнесортымский", "Междуреченский", "Солнечный","Новоаганск"]
            nao_cities = ["Нарьян-Мар", "Несь", "Поселок Искателей", "Красное"]
            chao_cities = ["Анадырь", "Билибино", "Певек", "Беринговский", "Мыс Шмидта", "Провидения", "Угольные Копи", "Эгвекинот"]
            eao_cities = ["Биробиджан", "Облучье", "Николаевка", "Ленинское", "Смидович", "Бабстово", "Амурзет", 
                "Теплоозерск", "Приамурский", "Птичник", "Бира"]
            crimea_cities = ["Алупка", "Алушта", "Андреевка", "Баланово", "Бахчисарай", "Баштановка", "Белая Скала",
                "Белогорск", "Береговое", "Бугаз", "Верхоречье", "Веселое", "Вилино", "Виноградное", "Водное", "Гаспра",
                "Генеральское", "Глазовка", "Грушевка", "Гурзуф", "Джанкой", "Евпатория", "Заветное", "Залесное", "Запрудное",
                "Заречное", "Зеленогорье", "Знаменское", "Зуя", "Ивановка", "Инкерман", "Каменское", "Карасевка",
                "Керчь", "Кизиловое", "Кипарисное", "Коктебель", "Колхозное", "Константиновка", "Кореиз", "Котовское",
                "Краснокаменка", "Красноперекопск", "Красноселовка", "Курортное", "Ласпи", "Левадки", "Ливадия",
                "Лучистое", "Любимовка", "Малореченское", "Малый Маяк", "Марьевка", "Массандра", "Медведево",
                "Межводное", "Мирный", "Мисхор", "Морозовка", "Морское", "Мраморное", "Набережное", "Нагорное",
                "Наниково", "Научный", "Нижнегорский", "Никита", "Новобобровка", "Новый Свет", "Оборонное",
                "Оленевка", "Орджоникидзе", "Ореанда", "Партенит", "Партизанское", "Первомайское", "Перевальное",
                "Передовое", "Пионерское", "Поворотное", "Подмаячный", "Портовое", "Предущелье", "Прибрежное",
                "Приветное", "Пролетарка", "Резервное", "Родниково", "Родниковое", "Рыбачье", "Саки",
                "Симеиз", "Симферополь", "Синапное", "Скалистое", "Славное", "Советское", "Соколиное", "Староселье",
                "Старый Крым", "Стерегущее", "Судак", "Счастливое", "Танковое", "Терновка", "Томашовка", "Утес",
                "Учкуевка", "Феодосия", "Ферсманово", "Форос", "Фруктовое", "Фрунзе", "Ходжа-Сала", "Холмовка",
                "Цветущее", "Челядиново", "Черемисовка", "Черноморское", "Черноречье", "Чистополье", "Щебетовка",
                "Щелкино", "Яковенково", "Ялта",
                "Балаклава", "Севастополь"] # у меня есть geojson только для Крыма целиком, а не отдельно Крым и города фед. зн. Севастополя
            kherson_cities = ["Алешки", "Берислав", "Геническ", "Голая Пристань", "Каховка", "Новая Каховка", "Скадовск", "Таврийск", "Херсон"]
            donetsk_cities = ["Авдеевка", "Амвросиевка", "Бахмут", "Артемовск", "Белицкое", "Белозерское", "Волноваха", "Горловка", "Горняк", 
                "Дебальцево", "Доброполье", "Докучаевск", "Донецк", "Дружковка", "Енакиево", "Ждановка", "Зализное", "Артемово", "Зугрэс", 
                "Иловайск", "Кальмиусское", "Комсомольское", "Константиновка", "Краматорск", "Красногоровка", "Крестовка", "Кировское", "Курахово", 
                "Лиман", "Красный Лиман", "Макеевка", "Мариуполь", "Марьинка", "Мирноград", "Димитров", "Моспино", "Николаевка", "Новоазовск", 
                "Новогродовка", "Покровск", "Красноармейск", "Родинское", "Светлодарск", "Святогорск", "Северск", "Селидово", "Славянск", "Снежное", 
                "Соледар", "Чистяково", "Торез", "Торецк", "Дзержинск", "Углегорск", "Угледар", "Украинск", "Харцызск", "Часов Яр", "Шахтерск", 
                "Бунге", "Юнокоммунаровск", "Ясиноватая"]
            lugansk_cities = ["Александровск", "Алмазная", "Алчевск", "Антрацит", "Артемовск", "Брянка", "Вахрушево", 
                "Горское", "Зимогорье", "Золотое", "Зоринск", "Ирмино", "Кировск", "Краснодон", "Красный Луч", "Кременная", "Лисичанск", 
                "Луганск", "Лутугино", "Миусинск", "Молодогвардейск", "Новодружеск", "Первомайск", "Перевальск", "Петровское", "Попасная", 
                "Приволье", "Ровеньки", "Рубежное", "Сватово", "Свердловск", "Северодонецк", "Старобельск", "Стаханов", "Суходольск", 
                "Счастье", "Червонопартизанск"]
            zaporozhye_cities = ["Бердянск", "Васильевка", "Вольнянск", "Гуляйполе", "Днепрорудное", "Запорожье", 
                "Каменка-Днепровская", "Мелитополь", "Молочанск", "Орехов", "Пологи", "Приморск", "Токмак", "Энергодар"]

            location_cache = {}
            for city in all_urls['rus_location']:
                if city in location_cache:
                    continue
                elif city in yanao_cities:
                    location_cache[city] = "Ямало-Ненецкий автономный округ"
                elif city in hmao_cities:
                    location_cache[city] = "Ханты-Мансийский автономный округ - Югра"
                elif city in nao_cities:
                    location_cache[city] = "Ненецкий автономный округ"
                elif city in chao_cities:
                    location_cache[city] = "Чукотский автономный округ"
                elif city in eao_cities:
                    location_cache[city] = "Еврейская автономная область"
                elif city in crimea_cities:
                    location_cache[city] = "Республика Крым"
                elif city in kherson_cities:
                    location_cache[city] = "Херсонская область"
                elif city in donetsk_cities:
                    location_cache[city] = "Донецкая область"
                elif city in lugansk_cities:
                    location_cache[city] = "Луганская область"
                elif city in zaporozhye_cities:
                    location_cache[city] = "Запорожская область"
                else:
                    try:
                        if ", " not in city:
                            if city != "Ватутинки" and city != "Кудрово" and city != "Глебовский":
                                df = nomi.query_location(city)
                                if df is not None and "state_name" in df.columns:
                                    most_common_state = df["state_name"].value_counts().idxmax()
                                    if most_common_state == "Камчатская Область":
                                        most_common_state = "Камчатский Край"
                                    location_cache[city] = most_common_state
                                else:
                                    location_cache[city] = "Регион не найден 1"
                            elif city == "Ватутинки":
                                location_cache[city] = "Москва"
                            elif city == "Глебовский":
                                location_cache[city] = "Московская Область"
                            else:
                                location_cache[city] = "Ленинградская Область"
                        else:
                            location_cache[city] = city[:city.index(",")]
                    except:
                        location_cache[city] = "Регион не найден 2"

            all_urls['federal_subject'] = all_urls['rus_location'].map(location_cache)

            global results_data
            results_data = analysis_modeling(all_urls)

            all_urls['grade'] = all_urls['grade'].str.replace(',', '.')
            all_urls['grade'] = pd.to_numeric(all_urls['grade'], errors='coerce')
            global plots
            plots = analysis_plotting(all_urls)

            global geomaps
            geomaps = analysis_plotting_map(all_urls)
            
            if plots:
                plotting_status = '✅'
            if results_data:
                modeling_status = '✅'
            if geomaps:
                plotting_status_map = '✅'
                
            # Теперь переадресация на главную страницу
            return redirect(url_for('index'))

        else: # Если, например, название вбито некорректно
            warning = "Товары не найдены. Вернитесь на страницу поиска."
            modeling_status = ''
            plotting_status = ''
            plotting_status_map = ''
            return render_warning("Товары не найдены. Вернитесь на страницу поиска.")

    # GET запрос, рендерим index с обновленными статусами
    return render_template('index.html', plotting_status_map=plotting_status_map, plotting_status=plotting_status, modeling_status=modeling_status, data_ready=data_ready)

@app.route('/progress')
def progress_update():
    def generate():
        while progress["current"] < progress["total"] and progress["current"] > 0.0:
            percent = int((progress["current"] / progress["total"]) * 100)
            yield f"data: {percent}\n\n"
            time.sleep(0.5)  # Adjust this delay based on update frequency needed
    return Response(generate(), mimetype='text/event-stream')

@app.route('/map')
def map():
    if geomaps:
        return render_template('geo.html', queries=queries_for_html, geomaps=geomaps, modeling_status=modeling_status, plotting_status=plotting_status, data_ready=data_ready, plotting_status_map=plotting_status_map)
    elif plotting_status_map == '⏳':
        return render_warning("Товары загружаются...")
    else:
        return render_warning("Товары не выбраны. Вернитесь на страницу поиска.")

@app.route('/plotting')
def plotting():
    if plots:
        return render_template('plotting.html', queries=queries_for_html, plots=plots, modeling_status=modeling_status, plotting_status=plotting_status, data_ready=data_ready, plotting_status_map=plotting_status_map)
    elif plotting_status == '⏳':
        return render_warning("Товары загружаются...")
    else:
        return render_warning("Товары не выбраны. Вернитесь на страницу поиска.")

@app.route('/modeling')
def modeling():
    if results_data:
        return render_template('modeling.html', queries=queries_for_html, models_results=results_data, modeling_status=modeling_status, plotting_status=plotting_status, data_ready=data_ready, plotting_status_map=plotting_status_map)
    elif modeling_status == '⏳':
        return render_warning("Товары загружаются...")
    else:
        return render_warning("Товары не выбраны. Вернитесь на страницу поиска.")

@app.route('/download_csv')
def download_csv():
    if not data_ready or not output_filename:
        return redirect(url_for('index'))

    write_to_csv(all_urls, filename=output_filename)
    return send_file(output_filename, as_attachment=True, mimetype='text/csv', download_name=output_filename)

@app.route('/reset', methods=['POST'])
def reset():
    global plotting_status_map, plotting_status, modeling_status, data_ready, results_data, plots, output_filename, reset_button, geomaps
    reset_button = True
    plotting_status_map = ''
    plotting_status = ''
    modeling_status = ''
    data_ready = False
    results_data = None
    plots = None
    geomaps = None
    output_filename = None
    #all_urls = None
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)