import re

# Попытка создать словарь со специальными случаями вроде наличия мягкого знака при обратной транслитерации :)
special_cases = {
    'abez': 'Абезь',
    'aigun': 'Айгунь',
    'alatyr': 'Алатырь',
    'anadyr': 'Анадырь',
    'andreapol': 'Андреаполь',
    'aramil': 'Арамиль',
    'arkul': 'Аркуль',
    'arshan': 'Аршань',
    'astrahan': 'Астрахань',
    'bogatyr': 'Богатырь',
    'bolon': 'Болонь',
    'bolshoy kamen': 'Большой Камень',
    'budogoshch': 'Будогощь',
    'bursol': 'Бурсоль',
    'bytoshch': 'Бытошь',
    'verkhnya sysert': 'Верхняя Сысерть',
    'vozhaiel': 'Вожаель',
    'gergebil': 'Гергебиль',
    'elan': 'Елань',
    'epifan': 'Епифань',
    'ermishch': 'Ермишь',
    'zalegoshch': 'Залегощь',
    'ivdel': 'Ивдель',
    'idel': 'Идель',
    'iraiel': 'Ираель',
    'isilkule': 'Исилькуль',
    'kazan': 'Казань',
    'karaidel': 'Караидель',
    'kargopol': 'Каргополь',
    'kem': 'Кемь',
    'kerch': 'Керчь',
    'kilmez': 'Кильмезь',
    'kinel': 'Кинель',
    'kolyvan': 'Колывань',
    'kondol': 'Кондоль',
    'lebedyan': 'Лебедянь',
    'likhoslavl': 'Лихославль',
    'lokot': 'Локоть',
    'lyambir': 'Лямбирь',
    'medyn': 'Медынь',
    'mezen': 'Мезень',
    'mukhorshibir': 'Мухоршибирь',
    'nazran': 'Назрань',
    'nevel': 'Невель',
    'nikel': 'Никель',
    'novaya usman': 'Новая Усмань',
    'novosil': 'Новосиль',
    'nyagan': 'Нягань',
    'oboyan': 'Обоянь',
    'parabel': 'Парабель',
    'paren': 'Парень',
    'permyshl': 'Перемышль',
    'perm': 'Пермь',
    'pristen': 'Пристень',
    'ramon': 'Рамонь',
    'roslavl': 'Рославль',
    'rossosh': 'Россошь',
    'roshal': 'Рошаль',
    'ryazan': 'Рязань',
    'sevastopol': 'Севастополь',
    'simferopol': 'Симферополь',
    'sovetskaya gavan': 'Советская Гавань',
    'stavropol': 'Ставрополь',
    'stroitel': 'Строитель',
    'sudislavl': 'Судиславль',
    'suzdal': 'Суздаль',
    'sut-khol': 'Суть-Холь',
    'syzran': 'Сызрань',
    'sysert': 'Сысерть',
    'tver': 'Тверь',
    'tigilya': 'Тигиль',
    'tisul': 'Тисуль',
    'tyumen': 'Тюмень',
    'uren': 'Урень',
    'usman': 'Усмань',
    'ust-kishert': 'Усть-Кишерть',
    'ust-charyshskaya pristan': 'Усть-Чарышская Пристань',
    'khorol': 'Хороль',
    'chaltyr': 'Чалтырь',
    'chebarkul': 'Чебаркуль',
    'cherdyn': 'Чердынь',
    'chistopol': 'Чистополь',
    'sherbakul': 'Шербакуль',
    'elektrostal': 'Электросталь',
    'ertil': 'Эртиль',
    'yuruzan': 'Юрюзань',
    'yaroslavl': 'Ярославль',
    'yashkul': 'Яшкуль',
    'bratsk': 'Братск',
    'verkhneimbarsk': 'Верхнеимбатск',
    'irkutsk': 'Иркутск',
    'novovyatsk': 'Нововятск',
    'okhotsk': 'Охотск',
    'sovetsk': 'Советск',
    'ust-kamchatsk': 'Усть-Камчатск',
    'yakutsk': 'Якутск',
    'almenyevo': 'Альменево',
    'almetyevsk': 'Альметьевск',
    'arsenyev': 'Арсеньев',
    'arsenyevo': 'Арсеньево',
    'arhangelsk': 'Архангельск',
    'arhangelskoye': 'Архангельское',
    'arya': 'Арья',
    'atyuryevo': 'Атюрьево',
    'baikalsk': 'Байкальск',
    'basyanovskiy': 'Басьяновский',
    'bednodemyanovsk': 'Беднодемьяновск',
    'beltyrskiy': 'Бельтырский',
    'berdyuzhye': 'Бердюжье',
    'bolshaya_vishera': 'Большая Вишера',
    'bolshaya_glushchitsa': 'Большая Глущица',
    'bolshaya_izhora': 'Большая Ижора',
    'bolshaya_martynovka': 'Большая Мартыновка',
    'bolshaya_murta': 'Большая Мурта',
    'bolshaya_rechka': 'Большая Речка',
    'bolshaya_sosnova': 'Большая Соснова',
    'bolshaya_chernigovka': 'Большая Черниговка',
    'bolshivik': 'Большевик',
    'bolshereck': 'Большерецк',
    'bolsherechenesk': 'Большереченск',
    'bolsherecheye': 'Большеречье',
    'bolsheustikinskoe': 'Большеустьикинское',
    'bolshiye_berezniki': 'Большие Березники',
    'bolshiye_uki': 'Большие Уки',
    'bolshoe_boldino': 'Большое Болдино',
    'bolshoe_ignatovo': 'Большое Игнатово',
    'bolshoe_kozzino': 'Большое Козино',
    'bolshoe_murashkino': 'Большое Мурашкино',
    'bolshoe_nagatkino': 'Большое Нагаткино',
    'bolshoe_pikino': 'Большое Пикино',
    'bolshoe_polpino': 'Большое Полпино',
    'bolshoe_selo': 'Большое Село',
    'bolshoe_soldatskoye': 'Большое Солдатское',
    'bolshoe_sorokino': 'Большое Сорокино',
    'bolshoy_kamen': 'Большой Камень',
    'bolshoy_lug': 'Большой Луг',
    'bolshoy_uluy': 'Большой Улуй',
    'bugulma': 'Бугульма',
    'vasilyevo': 'Васильево',
    'vasilyevskiy moh': 'Васильевский Мох',
    'vasilsursk': 'Васильсурск',
    'veletma': 'Велетьма',
    'velsk': 'Вельск',
    'verhneuralsk': 'Верхнеуральск',
    'verhovazhye': 'Верховажье',
    'verhovye': 'Верховье',
    'verhoturye': 'Верхотурье',
    'verhoshizhemye': 'Верхошижемье',
    'vozhd proletariata': 'Вождь Пролетариата',
    'vozneseenie': 'Вознесенье',
    'volsk': 'Вольск',
    'vorobyovka': 'Воробьевка',
    'vyazma': 'Вязьма',
    'gorkiy': 'Горький',
    'gorkovskoye': 'Горьковское',
    'gurevsk': 'Гурьевск',
    'gus-hrustalnyy': 'Гусь Хрустальный',
    'dalnegorsk': 'Дальнегорск',
    'dalnee konstantinovo': 'Дальнее Константиново',
    'dalnerechensk': 'Дальнереченск',
    'daryinskoe': 'Дарьинское',
    'dmitriev-lgovskiy': 'Дмитриев-Льговский',
    'dovolnoye': 'Довольное',
    'duldurga': 'Дульдурга',
    'dyatkovo': 'Дятьково',
    'egoryevsk': 'Егорьевск',
    'elany-kolenovskiy': 'Елань-Коленовский',
    'elatma': 'Елатьма',
    'yelniki': 'Ельники',
    'yelnya': 'Ельня',
    'yeltsovka': 'Ельцовка',
    'emelyanova': 'Емельяново',
    'zabaykalsk': 'Забайкальск',
    'zavety ilyicha': 'Заветы Ильича',
    'zavolzhye': 'Заволжье',
    'zavyalovo': 'Завьялово',
    'zaplyusye': 'Заплюсье',
    'zarechye': 'Заречье',
    'zelenodolsk': 'Зеленодольск',
    'zolnoye': 'Зольное',
    'zyuzelskiy': 'Зюзельский',
    'ivankovskiy': 'Иваньковский',
    'izobilnyy': 'Изобильный',
    'ilinskiy': 'Ильинский',
    'ilinsko-podomskoye': 'Ильинско-Подомское',
    'ilinskoye-hovanskoye': 'Ильинское-Хованское',
    'ilka': 'Илька',
    'ilpyrskiy': 'Ильпырский',
    'ilsky': 'Ильский',
    'innokentyevka': 'Иннокентьевка',
    'isilkul': 'Исилькуль',
    'iulyitin': 'Иульитин',
    'kagalnitskaya': 'Кагальницкая',
    'kamensk-uralskiy': 'Каменск-Уральский',
    'kamen-na-obi': 'Камень-на-Оби',
    'kamen-rybolov': 'Камень-Рыболов',
    'kamskoe ustye': 'Камское Устье',
    'kananikolskoye': 'Кананикольское',
    'karaidelskiy': 'Караидельский',
    'kargapolye': 'Каргаполье',
    'kestenega': 'Кестеньга',
    'kilidinstroy': 'Кильдинстрой',
    'kilmez': 'Кильмезь',
    'kinel-cherkasy': 'Кинель-Черкасы',
    'klyazma': 'Клязьма',
    'kozelsk': 'Козельск',
    'kozulka': 'Козулька',
    'kozmodyemyansk': 'Козьмодемьянск',
    'kolchugino': 'Кольчугино',
    'komsomolsk': 'Комсомольск',
    'komsomolsk-na-amure': 'Комсомольск-на-Амуре',
    'komsomolskiy': 'Комсомольский',
    'komsomolskoe': 'Комсомольское',
    'kopyevo': 'Копьево',
    'kotelniki': 'Котельники',
    'kotelnikov': 'Котельниково',
    'kotelnich': 'Котельнич',
    'krasnoselkup': 'Красноселькуп',
    'krasnoturinsk': 'Краснотурьинск',
    'krasnouralsk': 'Красноуральск',
    'krasnousolsky': 'Красноусольский',
    'kunya': 'Кунья',
    'kurilsk': 'Курильск',
    'laryak': 'Ларьяк',
    'lahdenpohya': 'Лахденпохья',
    'lebyazhye': 'Лебяжье',
    'lysyva': 'Лысьва',
    'lvovskiy': 'Львовский',
    'lygovo': 'Льгов',
    'makaryev': 'Макарьев',
    'maloyarhangelsk': 'Малоархангельск',
    'mariupol': 'Мариуполь',
    'maryanovka': 'Марьяновка',
    'medvezhegorsk': 'Медвежьегорск',
    'melnikovo': 'Мельниково',
    'mehelta': 'Мехельта',
    'milkovо': 'Мильково',
    'mineralnye vody': 'Минеральные Воды',
    'mosalsk': 'Мосальск',
    'nalchik': 'Нальчик',
    'naryan-mar': 'Нарьян-Мар',
    'nevelsk': 'Невельск',
    'nevyansk': 'Невьянск',
    'nelkan': 'Нелькан',
    'nikolsk': 'Никольск',
    'nikolskoye': 'Никольское',
    'novosokolniki': 'Новосокольники',
    'novouralsk': 'Новоуральск',
    'novyy_toryal': 'Новый Торъял',
    'norilsk': 'Норильск',
    'noyabrsk': 'Ноябрьск',
    'obluchye': 'Облучье',
    'ozherelye': 'Ожерелье',
    'oktyabrsk': 'Октябрьск',
    'oktyabrsky': 'Октябрьский',
    'oktyabrskoye': 'Октябрьское',
    'olga': 'Ольга',
    'olhovatka': 'Ольховатка',
    'olhovka': 'Ольховка',
    'paranya': 'Параньга',
    'parfentyevo': 'Парфентьево',
    'pervouralsk': 'Первоуральск',
    'pereslavl-zalesskiy': 'Переславль-Залесский',
    'petrovsk-zabaykalskiy': 'Петровск-Забайкальский',
    'pilna': 'Пильна',
    'poddorye': 'Поддорье',
    'podolsk': 'Подольск',
    'podporozhye': 'Подпорожье',
    'poshehonye-volodarsk': 'Пошехонье-Володарск',
    'privokzalnyy': 'Привокзальный',
    'privolzhye': 'Приволжье',
    'priobye': 'Приобье',
    'prokopievsk': 'Прокопьевск',
    'pyt-yah': 'Пыть-Ях',
    'repyovka': 'Репьевка',
    'rovenki': 'Ровеньки',
    'rylsk': 'Рыльск',
    'salsk': 'Сальск',
    'severo-kurilsk': 'Северо-Курильск',
    'severo-baykalsk': 'Северобайкальск',
    'severo-uralsk': 'Североуральск',
    'sedelnikovо': 'Седельниково',
    'sinegorye': 'Синегорье',
    'sokolskoye': 'Сокольское',
    'solnechnodolskiy': 'Солнечнодольск',
    'sol-iletsk': 'Соль-Илецк',
    'solvichagodsk': 'Сольвычегодск',
    'soltsy': 'Сольцы',
    'sosva': 'Сосьва',
    'spassk-dalniy': 'Спасск-Дальний',
    'sredneuralsk': 'Среднеуральск',
    'staroyuryevo': 'Староюрьево',
    'talmenka': 'Тальменка',
    'tekstilshchik': 'Текстильщик',
    'telmana': 'Тельмана',
    'tengushevo': 'Теньгушево',
    'terengha': 'Тереньга',
    'tobolsk': 'Тобольск',
    'tolyatti': 'Тольятти',
    'totma': 'Тотьма',
    'tulskiy': 'Тульский',
    'tyulgan': 'Тюльган',
    'uvelskiy': 'Увельский',
    'udelnaya': 'Удельная',
    'ulyanovo': 'Ульяново',
    'ulyanovsk': 'Ульяновск',
    'uralsk': 'Уральск',
    'usolie': 'Усолье',
    'usole-sibirskoe': 'Усолье-Сибирское',
    'ust-avam': 'Усть-Авам',
    'ust-belaya': 'Усть-Белая',
    'ust-bolshereck': 'Усть-Большерецк',
    'ust-dzheguta': 'Усть-Джегута',
    'ust-donetskiy': 'Усть-Донецкий',
    'ust-ilimsk': 'Усть-Илимск',
    'ust-ishim': 'Усть-Ишим',
    'ust-kalmanka': 'Усть-Калманка',
    'ust-kamchatsk': 'Усть-Камчатск',
    'ust-kan': 'Усть-Кан',
    'ust-katav': 'Усть-Катав',
    'ust-kisherte': 'Усть-Кишерть',
    'ust-koksa': 'Усть-Кокса',
    'ust-kulom': 'Усть-Кулом',
    'ust-kut': 'Усть-Кут',
    'ust-labinsk': 'Усть-Лабинск',
    'ust-maya': 'Усть-Мая',
    'ust-nera': 'Усть-Нера',
    'ust-omchug': 'Усть-Омчуг',
    'ust-ordynskiy': 'Усть-Ордынский',
    'ust-tarka': 'Усть-Тарка',
    'ust-uda': 'Усть-Уда',
    'ust-ulagan': 'Усть-Улаган',
    'ust-tsylma': 'Усть-Цильма',
    'ust-charyshskaya pristana': 'Усть-Чарышская Пристань',
    'hotkovo': 'Хотьково',
    'hoholskiy': 'Хохольский',
    'tsivilsk': 'Цивильск',
    'sharya': 'Шарья',
    'shahunya': 'Шахунья',
    'sheremetevskiy': 'Шереметьевский',
    'shlisselburg': 'Шлиссельбург',
    'shchuchye': 'Щучье',
    'engels': 'Энгельс',
    'yuzhno-kurilsk': 'Южно-Курильск',
    'yuzhno-uralsk': 'Южно-Уральск',
    'yuryev-polskiy': 'Юрьев-Польский',
    'yuryevets': 'Юрьевец',
    'yurya': 'Юрья',
    'yusva': 'Юсьва',
    'yakshur-bodya': 'Якшур-Бодья',
    'yalchiki': 'Яльчики'
    }

def convert_to_cyrillic(location):
    """
    Описание: возвращает название города на кириллице.

    Args:
        location (str): город на латинице, samara, nizhniy_novgorod, и тд.

    Returns:
        location (str): город на кириллице, Самара, Нижний Новгород, и тд.
    """

    if location in special_cases:
        return special_cases[location]

    # Если не специальный случай:
    latin_to_cyrillic = {
        'A': 'А', 'B': 'Б', 'V': 'В', 'G': 'Г', 'D': 'Д', 'E': 'Е', 'Yo': 'Ё',
        'Zh': 'Ж', 'Z': 'З', 'I': 'И', 'Y': 'Й', 'K': 'К', 'L': 'Л', 'M': 'М',
        'N': 'Н', 'O': 'О', 'P': 'П', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
        'F': 'Ф', 'H': 'Х', 'Ts': 'Ц', 'Ch': 'Ч', 'Sh': 'Ш', 'Sch': 'Щ', 
        'Yu': 'Ю', 'Ya': 'Я', 'a': 'а', 'b': 'б', 'v': 'в', 'g': 'г', 'd': 'д', 
        'e': 'е', 'yo': 'ё', 'zh': 'ж', 'z': 'з', 'i': 'и', 'y': 'ы', 'k': 'к', 
        'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'r': 'р', 's': 'с', 
        't': 'т', 'u': 'у', 'f': 'ф', 'h': 'х', 'ts': 'ц', 'ch': 'ч', 'sh': 'ш', 
        'sch': 'щ', 'yu': 'ю', 'ya': 'я'
    }

    def transliterate_to_cyrillic(text):
        result = []
        i = 0
        while i < len(text):
            # Check for two-letter combinations (e.g., 'Zh', 'Ch') first
            if i + 1 < len(text) and text[i:i+2] in latin_to_cyrillic:
                result.append(latin_to_cyrillic[text[i:i+2]])
                i += 2  # Move past the two-letter combination
            # Check for one-letter mappings
            elif text[i] in latin_to_cyrillic:
                result.append(latin_to_cyrillic[text[i]])
                i += 1
            # If no mapping found, keep the character as is
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
    location = transliterate_to_cyrillic(location)
    # Слова с заглавной буквы, кроме случаев вроде "Ростов-на-Дону". Сюда же входят остальные найденные мной ошибки.
    location = location.title()
    location = re.sub(r'-На-', '-на-', location)
    location = re.sub(r'иы', 'ий', location)
    location = re.sub(r'уы', 'уй', location)
    location = re.sub(r'ыу', 'ю', location)
    location = re.sub(r'ыа', 'я', location)
    location = re.sub(r'еы', 'ей', location)
    location = re.sub(r'Еы', 'Ей', location)
    location = re.sub(r'Област', 'область,', location)
    location = re.sub(r'Край', 'край,', location)
    location = re.sub(r'ыы', 'ый', location)
    location = re.sub(r'Ыу', 'Ю', location)
    location = re.sub(r'Ыа', 'Я', location)
    location = re.sub(r'_', ' ', location)
    location = re.sub(r'аы', 'ай', location)
    location = re.sub(r'оы', 'ой', location)
    location = re.sub(r'Уы', 'Уй', location)
    location = re.sub(r'уы', 'уй', location)
    location = re.sub(r'Ставрополский', 'Ставропольский', location)
    
    location = re.sub(r'Петербург ', 'Петербург, ', location)
    location = re.sub(r'Москва ', 'Москва, ', location)
    location = re.sub(r'Москва ', 'Москва, ', location)
    location = re.sub(r'Саха Якутия ', 'Саха (Якутия) Республика, ', location)
    location = re.sub(r'Дагестан ', 'Дагестан Республика, ', location)
    location = re.sub(r'Башкортостан ', 'Башкортостан Республика, ', location)
    location = re.sub(r'Край ', 'Край, ', location)

    location = re.sub(r'Егоревск', 'Егорьевск', location)
    location = re.sub(r'Месчовск', 'Мещовск', location)
    location = re.sub(r'Мышако', 'Мысхако', location)
    location = re.sub(r'ийа', 'ия', location)
    location = re.sub(r'Ыошкар-Ола', 'Йошкар-Ола', location)
    location = re.sub(r'Ёшкар-Ола', 'Йошкар-Ола', location)
    location = re.sub(r'Елиста', 'Элиста', location)
    location = re.sub(r'Улан-Уде', 'Улан-Удэ', location)
    location = re.sub(r'Минералные Воды', 'Минеральные Воды', location)
    location = re.sub(r'Прокопевск', 'Прокопьевск', location)
    location = re.sub(r'Гулкевичи', 'Гулькевичи', location)
    location = re.sub(r'Алметевск', 'Альметьевск', location)
    location = re.sub(r'Мытисчи', 'Мытищи', location)
    location = re.sub(r'Благовесченск', 'Благовещенск', location)
    location = re.sub(r'Счекино', 'Щекино', location)
    location = re.sub(r'Счелково', 'Щелково', location)
    location = re.sub(r'Петропавловск-Камчацкий', 'Петропавловск-Камчатский', location)
    location = re.sub(r'Счербинка', 'Щербинка', location)
    location = re.sub(r'Електро', 'Электро', location)
    location = re.sub(r'Илский', 'Ильский', location)
    location = re.sub(r'Акяр', 'Акяр', location)
    
    return location