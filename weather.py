import json
import requests


def get_name_country(country_code):
    m = {
        'AU': 'Австралія',
        'AT': 'Австрія',
        'AZ': 'Азербайджан',
        'AX': 'Аландські острови',
        'AL': 'Албанія',
        'DZ': 'Алжир',
        'AS': 'Американське Самоа',
        'VI': 'Американські Віргінські Острови',
        'AI': 'Ангілья',
        'AO': 'Ангола',
        'AD': 'Андорра',
        'AQ': 'Антарктида',
        'AG': 'Антигуа і Барбуда',
        'AR': 'Аргентина',
        'AW': 'Аруба',
        'AF': 'Афганістан',
        'BS': 'Багамські Острови',
        'BD': 'Бангладеш',
        'BB': 'Барбадос',
        'BH': 'Бахрейн',
        'BZ': 'Беліз',
        'BE': 'Бельгія',
        'BJ': 'Бенін',
        'BM': 'Бермудські Острови',
        'BY': 'Білорусь',
        'BG': 'Болгарія',
        'BO': 'Болівія',
        'BA': 'Боснія і Герцеговина',
        'BW': 'Ботсвана',
        'BR': 'Бразилія',
        'IO': 'Британська Територія в Індійському Океані',
        'VG': 'Британські Віргінські Острови',
        'BN': 'Бруней',
        'BF': 'Буркіна-Фасо',
        'BI': 'Бурунді',
        'BT': 'Бутан',
        'VU': 'Вануату',
        'VA': 'Ватикан',
        'GB': 'Велика Британія',
        'VE': 'Венесуела',
        'VN': 'В''єтнам',
        'AM': 'Вірменія',
        'WF': 'Волліс і Футуна',
        'GA': 'Габон',
        'HT': 'Гаїті',
        'GY': 'Гаяна',
        'GM': 'Гамбія',
        'GH': 'Гана',
        'GP': 'Гваделупа',
        'GT': 'Гватемала',
        'GN': 'Гвінея',
        'GW': 'Гвінея-Бісау',
        'GG': 'Гернсі',
        'HN': 'Гондурас',
        'HK': 'Гонконг',
        'GD': 'Гренада',
        'GR': 'Греція',
        'GE': 'Грузія',
        'GU': 'Гуам',
        'GI': 'Гібралтар',
        'GL': 'Гренландія',
        'DK': 'Данія',
        'CD': 'ДР Конго',
        'JE': 'Джерсі',
        'DJ': 'Джибуті',
        'DM': 'Домініка',
        'DO': 'Домініканська Республіка',
        'UM': 'Зовнішні малі острови США',
        'EC': 'Еквадор',
        'GQ': 'Екваторіальна Гвінея',
        'ER': 'Еритрея',
        'EE': 'Естонія',
        'ET': 'Ефіопія',
        'EG': 'Єгипет',
        'YE': 'Ємен',
        'ZM': 'Замбія',
        'EH': 'Західна Сахара',
        'ZW': 'Зімбабве',
        'IL': 'Ізраїль',
        'IN': 'Індія',
        'ID': 'Індонезія',
        'IQ': 'Ірак',
        'IR': 'Іран',
        'IE': 'Ірландія',
        'IS': 'Ісландія',
        'ES': 'Іспанія',
        'IT': 'Італія',
        'JO': 'Йорданія',
        'CV': 'Кабо-Верде',
        'KZ': 'Казахстан',
        'KY': 'Кайманові Острови',
        'KH': 'Камбоджа',
        'CM': 'Камерун',
        'CA': 'Канада',
        'QA': 'Катар',
        'KE': 'Кенія',
        'KG': 'Киргизстан',
        'CN': 'Китайська Народна Республіка',
        'CY': 'Кіпр',
        'KI': 'Кірибаті',
        'CC': 'Кокосові острови',
        'CO': 'Колумбія',
        'KM': 'Коморські Острови',
        'CG': 'Республіка Конго',
        'CR': 'Коста-Рика',
        'CI': 'Кот-д''Івуар',
        'CU': 'Куба',
        'KW': 'Кувейт',
        'CW': 'Кюрасао',
        'LA': 'Лаос',
        'LV': 'Латвія',
        'LS': 'Лесото',
        'LT': 'Литва',
        'LR': 'Ліберія',
        'LB': 'Ліван',
        'LY': 'Лівія',
        'LI': 'Ліхтенштейн',
        'LU': 'Люксембург',
        'MU': 'Маврикій',
        'MR': 'Мавританія',
        'MG': 'Мадагаскар',
        'YT': 'Майотта',
        'MO': 'Макао',
        'MW': 'Малаві',
        'MY': 'Малайзія',
        'ML': 'Малі',
        'MV': 'Мальдіви',
        'MT': 'Мальта',
        'MA': 'Марокко',
        'MQ': 'Мартиніка',
        'MH': 'Маршаллові Острови',
        'MX': 'Мексика',
        'MZ': 'Мозамбік',
        'MD': 'Молдова',
        'MC': 'Монако',
        'MN': 'Монголія',
        'MS': 'Монтсеррат',
        'MM': 'М''янма',
        'NA': 'Намібія',
        'NR': 'Науру',
        'NP': 'Непал',
        'NE': 'Нігер',
        'NG': 'Нігерія',
        'NL': 'Нідерланди',
        'AN': 'Нідерландські Антильські острови',
        'BQ': 'Карибські Нідерланди',
        'NI': 'Нікарагуа',
        'DE': 'Німеччина',
        'NU': 'Ніуе',
        'NZ': 'Нова Зеландія',
        'NC': 'Нова Каледонія',
        'NO': 'Норвегія',
        'AE': 'ОАЕ',
        'OM': 'Оман',
        'BV': 'Острів Буве',
        'IM': 'Острів Мен',
        'NF': 'Острів Норфолк',
        'CX': 'Острів Різдва',
        'SH': 'Острови Святої Єлени, Вознесіння і Тристан-да-Кунья',
        'HM': 'Острів Херд і острови Макдональд',
        'CK': 'Острови Кука',
        'PK': 'Пакистан',
        'PW': 'Палау',
        'PS': 'Палестина',
        'PA': 'Панама',
        'PG': 'Папуа Нова Гвінея',
        'PY': 'Парагвай',
        'PE': 'Перу',
        'ZA': 'ПАР',
        'GS': 'Південна Джорджія та Південні Сандвічеві Острови',
        'KR': 'Південна Корея',
        'SS': 'Південний Судан',
        'KP': 'Північна Корея',
        'MK': 'Північна Македонія',
        'MP': 'Північні Маріанські Острови',
        'PN': 'Піткерн',
        'PL': 'Польща',
        'PT': 'Португалія',
        'PR': 'Пуерто-Рико',
        'RE': 'Реюньйон',
        'RU': 'Росія',
        'RW': 'Руанда',
        'RO': 'Румунія',
        'SV': 'Сальвадор',
        'WS': 'Самоа',
        'SM': 'Сан-Марино',
        'ST': 'Сан-Томе і Принсіпі',
        'SA': 'Саудівська Аравія',
        'SZ': 'Есватіні',
        'SJ': 'Свальбард і Ян-Маєн',
        'SC': 'Сейшельські Острови',
        'BL': 'Сен-Бартелемі',
        'SN': 'Сенегал',
        'MF': 'Сен-Мартен',
        'PM': 'Сен-П''єр і Мікелон',
        'VC': 'Сент-Вінсент і Гренадини',
        'KN': 'Сент-Кіттс і Невіс',
        'LC': 'Сент-Люсія',
        'RS': 'Сербія',
        'SY': 'Сирія',
        'SG': 'Сінгапур',
        'SX': 'Сінт-Мартен',
        'SK': 'Словаччина',
        'SI': 'Словенія',
        'SB': 'Соломонові Острови',
        'SO': 'Сомалі',
        'US': 'США',
        'SD': 'Судан',
        'SR': 'Суринам',
        'TL': 'Східний Тимор',
        'SL': 'Сьєрра-Леоне',
        'TJ': 'Таджикистан',
        'TH': 'Таїланд',
        'TW': 'Тайвань',
        'TZ': 'Танзанія',
        'TC': 'Острови Теркс і Кайкос',
        'TG': 'Того',
        'TK': 'Токелау',
        'TO': 'Тонга',
        'TT': 'Тринідад і Тобаго',
        'TV': 'Тувалу',
        'TN': 'Туніс',
        'TR': 'Туреччина',
        'TM': 'Туркменістан',
        'UG': 'Уганда',
        'HU': 'Угорщина',
        'UZ': 'Узбекистан',
        'UA': 'Україна',
        'UY': 'Уругвай',
        'FO': 'Фарерські острови',
        'FM': 'Федеративні Штати Мікронезії',
        'FJ': 'Фіджі',
        'PH': 'Філіппіни',
        'FI': 'Фінляндія',
        'FK': 'Фолклендські Острови',
        'FR': 'Франція',
        'GF': 'Французька Гвіана',
        'PF': 'Французька Полінезія',
        'TF': 'Французькі Південні і Антарктичні Території',
        'HR': 'Хорватія',
        'CF': 'Центральноафриканська Республіка',
        'TD': 'Чад',
        'CZ': 'Чехія',
        'CL': 'Чилі',
        'ME': 'Чорногорія',
        'CH': 'Швейцарія',
        'SE': 'Швеція',
        'LK': 'Шрі-Ланка',
        'JM': 'Ямайка',
        'JP': 'Японія'
    }
    try:
        country_name = m[country_code]
    except Exception as err:
        country_name = country_code
        print(err)
    return country_name


# Функция получения погоды с сайта openweathermap.org
class Read_weather:
    def __init__(self, city_name):
        self.city_not_found = False
        self.text_error = ""
        self.text_result = ""
        try:
            # read token to access the HTTP API
            file = open(file='secret_key.json', mode="r", encoding="utf8")
            data = json.loads(file.read())
            token_key = data['openweathermap_key']

            url = (f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&lang=ua&appid='
                   f'{token_key}')
            response = requests.get(url)
            data = json.loads(response.text)
            if str(data['cod']) == "200":
                self.text_result = ("Місто - " + str(city_name) + " (знайдене - " + str(data['name']) +
                                    "(" + str(get_name_country(data['sys']['country'])) + "))\n" +
                                    "Температура: " + str(data['main']['temp']) +
                                    " °C (min: " + str(data['main']['temp_min']) +
                                    " °C, max: " + str(data['main']['temp_max']) + " °C)\n" +
                                    "Швидкість вітру: " + str(data['wind']['speed']) + " m/c\n" +
                                    "Вологість: " + str(data['main']['humidity']) + " %"
                                    )
            elif str(data['cod']) == "404":
                self.city_not_found = True
                self.text_error = 'Ошибка = ' + str(data['cod']) + ' ' + str(data['message'])
            else:
                self.text_error = 'Ошибка = ' + str(data['cod']) + ' ' + str(data['message'])

        except Exception as err_curs:
            self.text_error = err_curs
            print(self.text_error)
