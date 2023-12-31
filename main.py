import time
import telebot
import logging
from telebot import types
import emoji  # https://carpedm20.github.io/emoji/
from datetime import date
from datetime import datetime
from service.curs import Read_curs
from service.convert_curs import Read_convert_curs
from service.weather import Read_weather
from service.erb import Read_erb
from service.securities import Read_ISIN_Securities, get_name_securities_type
from settings import settings

bot = telebot.TeleBot(settings.bots.TELEGRAM_TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Головне Меню"),
    telebot.types.BotCommand("/curs", "Курси валют"),
    telebot.types.BotCommand("/convert_curs", "Конвертер валют"),
    telebot.types.BotCommand("/weather", "Погода"),
    telebot.types.BotCommand("/erb", "Виконавчі провадження"),
    telebot.types.BotCommand("/securities", "Цінні папери")
])
logger = telebot.logger
logging.basicConfig(filename='./log/filename.log', level=logging.DEBUG,
                    format="%(asctime)s - [%(levelname)s] - %(name)s - "
                           "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

# global variables
global_convert_code_from = ''
global_convert_code_to = ''
global_securities_type = ''

g_InlineKeyboard = True


#########################################################################
# commands=['start']
#########################################################################
@bot.message_handler(commands=['start'])
def start(message):
    message_text = (f'Привіт {emoji.emojize(":grinning_face:")}'
                    f' <b>{message.from_user.first_name} '
                    f'{message.from_user.last_name}'
                    f'</b> обери пункт з головного меню.')
    on_global_menu(message, message_text)
    # следующий шаг обработки
    bot.register_next_step_handler(message, on_click_start)


#########################################################################
# commands
#########################################################################
@bot.message_handler(commands=['curs', 'convert_curs', 'weather', 'erb', 'securities'])
def comm(message):
    on_click_start(message)


#########################################################################
# global menu
#########################################################################
def on_global_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":money_bag:")}'
                                f' Курси валют')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":currency_exchange:")}'
                                f' Конвертер валют')
    markup.add(btn1, btn2)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":rolled-up_newspaper:")}'
                                f' Цінні папери')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":check_box_with_check:")}'
                                f' Виконавчі провадження')
    markup.add(btn1, btn2)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":sun_behind_small_cloud:")}'
                                f' Погода')
    markup.add(btn1)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# on_click_global
#########################################################################
def on_click_global(message):
    message_text = f'{emoji.emojize(":house:")}...'
    on_global_menu(message, message_text)
    bot.register_next_step_handler(message, on_click_start)


#########################################################################
# on_click_start
#########################################################################
def on_click_start(message):
    if message.text.endswith('Головне Меню') or message.text.lower() == "/start":
        start(message)

    if message.text.endswith('Курси валют') or message.text.lower() == "/curs":
        # выводим новое меню
        on_curs_menu(message, f'{emoji.emojize(":heavy_dollar_sign:")} Оберіть валюту')
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_curs)

    elif (message.text.endswith('Конвертер валют')
          or message.text.lower() == "/convert_curs"):
        # выводим новое меню
        on_convert_curs_menu(message,
                             f'{emoji.emojize(":heavy_dollar_sign:")} Оберіть валюти')
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_convert_curs)

    elif (message.text.endswith('Погода')
          or message.text.lower() == "/weather"):
        # выводим новое меню
        on_weather_menu(message,
                        f'{emoji.emojize(":cityscape:")} Оберіть місто')
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_weather)

    elif (message.text.endswith('Виконавчі провадження')
          or message.text.lower() == "/erb"):
        # выводим новое меню
        on_erb_menu(message,
                    f'{emoji.emojize(":magnifying_glass_tilted_right:")}'
                    f' Пошук...')
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки

    elif message.text.endswith('Цінні папери') or message.text.lower() == "/securities":
        # выводим новое меню
        on_securities_menu(message,
                           f'{emoji.emojize(":magnifying_glass_tilted_right:")}'
                           f' Пошук...')
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_securities)
    else:
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_start)


#########################################################################
# curs menu
#########################################################################
def on_curs_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('USD - Долар США')
    btn2 = types.KeyboardButton('EUR - ЄВРО')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('GBP - Фунт стерлінгів')
    btn2 = types.KeyboardButton('PLN - Польский злотий')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Інша валюта')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":house:")} Головне Меню')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# curs
#########################################################################
def on_click_curs(message):
    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)
    elif message.text in ('USD - Долар США', 'EUR - ЄВРО',
                          'GBP - Фунт стерлінгів', 'PLN - Польский злотий'):
        p = Read_curs(date.today(), message.text.upper()[0:3])
        if p.is_request_curs:
            bot.send_message(message.chat.id,
                             'Курс ' + message.text.upper()[0:3] + ' не найден')
        else:
            m_message = ('Курс ' + message.text.upper()[0:3] +
                         ' (' + p.curr_name + ')' +
                         " = {:.2f}".format(p.curs_amount) + ' грн.')
            # вызов меню курсов для повторного выбора
            on_curs_menu(message, m_message)
            # следующий шаг обработка курсов
            bot.register_next_step_handler(message, on_click_curs)

    elif message.text == 'Інша валюта':
        bot.send_message(message.chat.id, 'Введіть літерний код курсу валют')
        bot.register_next_step_handler(message, click_curs_others)


#########################################################################
# curs
#########################################################################
def click_curs_others(message):
    p = Read_curs(date.today(), message.text.upper())
    if p.is_request_curs:
        bot.send_message(message.chat.id, 'Курс ' + message.text.upper() +
                         ' не знайдений. Можна подивитись на сайті Код літерний	'
                         '- https://bank.gov.ua/ua/markets/exchangerates')
        bot.send_message(message.chat.id, 'Введіть новий літерний код курсу валют')
        bot.register_next_step_handler(message, click_curs_others)
    else:
        m_message = ('Курс ' + message.text.upper() + ' (' + p.curr_name + ')' +
                     " = {:.2f}".format(p.curs_amount) + ' грн.')
        # вызов меню курсов для повторного выбора
        on_curs_menu(message, m_message)
        # следующий шаг обработка курсов
        bot.register_next_step_handler(message, on_click_curs)


#########################################################################
# convert curs menu
#########################################################################
def on_convert_curs_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('USD->EUR')
    btn2 = types.KeyboardButton('USD->GBP')
    btn3 = types.KeyboardButton('USD->PLN')
    markup.add(btn1, btn2, btn3)
    btn1 = types.KeyboardButton('EUR->USD')
    btn2 = types.KeyboardButton('EUR->GBP')
    btn3 = types.KeyboardButton('EUR->PLN')
    markup.add(btn1, btn2, btn3)
    btn1 = types.KeyboardButton('GBP->USD')
    btn2 = types.KeyboardButton('GBP->EUR')
    btn3 = types.KeyboardButton('GBP->PLN')
    markup.add(btn1, btn2, btn3)
    btn1 = types.KeyboardButton('Інші валюти')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":house:")} Головне Меню')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# convert curs
#########################################################################
def on_click_convert_curs(message):
    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)
    elif message.text.count('->') > 0:
        p = message.text.split('->')
        global global_convert_code_from
        global global_convert_code_to
        global_convert_code_from = p[0]  # сохраняем коды валют для конвертации
        global_convert_code_to = p[1]  # сохраняем коды валют для конвертации
        #
        bot.send_message(message.chat.id, 'Введіть суму')
        bot.register_next_step_handler(message, click_convert_curs_amount)

    elif message.text == 'Інші валюти':
        bot.send_message(message.chat.id,
                         'Введіть коди валют для конвертації (наприклад USD/EUR)')
        bot.register_next_step_handler(message, click_convert_curs_others)


#########################################################################
# convert curs
#########################################################################
def click_convert_curs_amount(message):
    try:
        amount = float(message.text.strip().replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, 'Некоректне число. Введіть суму.')
        bot.register_next_step_handler(message, click_convert_curs_amount)
        return

    if amount > 0:
        cc = Read_convert_curs(amount, global_convert_code_from, global_convert_code_to)
        if cc.text_error != "":
            m_message = ('Конвертація пройшла з помилкою,'
                         ' можливо введені неправильні коди валют')
            on_convert_curs_menu(message, m_message)
            # следующий шаг обработки
            bot.register_next_step_handler(message, on_click_convert_curs)
            return

        m_message = ("{:.2f}".format(amount) + ' ' + global_convert_code_from + ' = '
                     + "{:.2f}".format(cc.curs_amount) + ' ' + global_convert_code_to)
        on_convert_curs_menu(message, m_message)
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_convert_curs)
    else:
        bot.send_message(message.chat.id, 'Введіть суму > 0.')
        bot.register_next_step_handler(message, click_convert_curs_amount)
        return


#########################################################################
# convert curs
#########################################################################
def click_convert_curs_others(message):
    try:
        m = message.text.strip().upper()
        p = m.split('/')
        global global_convert_code_from
        global global_convert_code_to
        global_convert_code_from = p[0].strip()  # сохраняем коды валют для конвертации
        global_convert_code_to = p[1].strip()  # сохраняем коды валют для конвертации
        #
        bot.send_message(message.chat.id, 'Введіть сумму')
        bot.register_next_step_handler(message, click_convert_curs_amount)
    except Exception as err_message:
        bot.send_message(message.chat.id,
                         'Введені некорректні коди валют'
                         ' для конвертації (наприклад USD/EUR)')
        bot.register_next_step_handler(message, click_convert_curs_others)
        print(err_message)


#########################################################################
# weather menu
#########################################################################
def on_weather_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('Київ')
    btn2 = types.KeyboardButton('Херсон')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Одеса')
    btn2 = types.KeyboardButton('Львів')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Інше місто')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":house:")} Головне Меню')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# weather
#########################################################################
def on_click_weather(message):
    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)
    elif message.text != 'Інше місто':
        p = Read_weather(message.text)
        if p.city_not_found:
            bot.send_message(message.chat.id, 'Місто ' + message.text + ' не знайдене')
        elif not p.city_not_found and p.text_error != "":
            bot.send_message(message.chat.id,
                             'Сервіс тимчасово не працює. Спробуйте пізніше.')
            on_click_global(message)
        else:
            m_message = p.text_result
            # вызов меню погоды для повторного выбора
            on_weather_menu(message, m_message)
            # следующий шаг обработки
            bot.register_next_step_handler(message, on_click_weather)

    elif message.text == 'Інше місто':
        bot.send_message(message.chat.id, 'Введіть назву міста')
        bot.register_next_step_handler(message, click_weather_others)


#########################################################################
# weather
#########################################################################
def click_weather_others(message):
    p = Read_weather(message.text)
    if p.city_not_found:
        bot.send_message(message.chat.id, 'Місто ' + message.text + ' не знайдене')
        bot.send_message(message.chat.id, 'Введіть нову назву міста (укр., eng. ...)')
        bot.register_next_step_handler(message, click_weather_others)
    elif not p.city_not_found and p.text_error != "":
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)
    else:
        m_message = p.text_result
        # вызов меню погоды для повторного выбора
        on_weather_menu(message, m_message)
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_weather)


#########################################################################
# erb menu
#########################################################################
def on_erb_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('Фіз. особа - код')
    btn2 = types.KeyboardButton('Фіз. особа - ПІБ')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Юр. особа - код')
    btn2 = types.KeyboardButton('Юр. особа - Назва')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":house:")} Головне Меню')
    markup.row(btn1)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# erb
#########################################################################
def on_click_erb(message):
    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)
    elif message.text == 'Фіз. особа - код':
        bot.send_message(message.chat.id, 'Введіть код фіз. особи')
        bot.register_next_step_handler(message, click_erb_fiz_code)
    elif message.text == 'Фіз. особа - ПІБ':
        bot.send_message(message.chat.id,
                         'Введіть дані фіз. особи через кому, наприклад \n'
                         'Миколайчук,Миколай,Миколайович,01.01.1982 \n'
                         'Миколайчук,Миколай,Миколайович \n'
                         'Миколайчук,Миколай \n')
        bot.register_next_step_handler(message, click_erb_fiz_name)
    elif message.text == 'Юр. особа - код':
        bot.send_message(message.chat.id, 'Введіть код юр. особи')
        bot.register_next_step_handler(message, click_erb_jur_code)
    elif message.text == 'Юр. особа - Назва':
        bot.send_message(message.chat.id, 'Введіть назву юр. особи')
        bot.register_next_step_handler(message, click_erb_jur_name)


#########################################################################
# erb
#########################################################################
def click_erb_fiz_code(message):
    if len(message.text) != 10:
        on_erb_menu(message, 'Код фіз. особи повинен = 10 символів')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_erb_fiz_code)
        return
    try:
        int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id,
                         'Код фіз. особи повинен мати тільки цифри.')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_erb_fiz_code)
        return

    cust_param = (message.text.strip(), "", "", "", None)
    p = Read_erb('phys', cust_param)
    if p.count_result == 0 and p.text_error == '':
        on_erb_menu(message, 'Виконавчі провадження не знайдені')
        # следующий шаг обработки
        bot.register_next_step_handler(message, on_click_erb)
    elif p.text_error != "":
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)
    else:
        m_message = p.text_result
        on_erb_menu(message, m_message)
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки


#########################################################################
# erb
#########################################################################
def click_erb_fiz_name(message):
    m_date = None
    m_surname = ""
    try:
        m = message.text.strip().split(",")
        if len(m) > 3:
            datetime.strptime(m[3].strip(), '%d.%m.%Y').date()
            m_date = m[3].strip()
        if len(m) > 2:
            m_surname = m[2].strip()
    except Exception as err_mes:
        bot.send_message(message.chat.id,
                         'Введені неправильні дані, прошу введіть повторно дані '
                         'фіз. особи через кому, наприклад \n'
                         'Миколайчук,Миколай,Миколайович,01.01.1982 \n'
                         'Миколайчук,Миколай,Миколайович \n'
                         'Миколайчук,Миколай \n')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_erb_fiz_name)
        print(err_mes)
        return
    cust_param = ("", m[0].strip(), m[1].strip(), m_surname, m_date)
    p = Read_erb('phys', cust_param)
    if p.count_result == 0 and p.text_error == '':
        on_erb_menu(message, 'Виконавчі провадження не знайдені')
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки
    elif p.text_error != "":
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)
    else:
        m_message = p.text_result
        on_erb_menu(message, m_message)
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки


#########################################################################
# erb
#########################################################################
def click_erb_jur_code(message):
    if len(message.text) != 8:
        on_erb_menu(message, 'Код юр. особи повинен = 8 символів')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_erb_jur_code)
        return
    try:
        int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Код юр. особи повинен мати тільки цифри.')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_erb_jur_code)
        return

    cust_param = (message.text.strip(), "", "", "", None)
    p = Read_erb('jur', cust_param)
    if p.count_result == 0 and p.text_error == '':
        on_erb_menu(message, 'Виконавчі провадження не знайдені')
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки
    elif p.text_error != "":
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)
    else:
        m_message = p.text_result
        on_erb_menu(message, m_message)
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки


#########################################################################
# erb
#########################################################################
def click_erb_jur_name(message):
    cust_param = ("", message.text.strip(), "", "", None)
    p = Read_erb('jur', cust_param)
    if p.count_result == 0 and p.text_error == '':
        on_erb_menu(message, 'Виконавчі провадження не знайдені')
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки
    elif p.text_error != "":
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)
    else:
        m_message = p.text_result
        on_erb_menu(message, m_message)
        bot.register_next_step_handler(message, on_click_erb)  # следующий шаг обработки


#########################################################################
# securities menu
#########################################################################
def on_securities_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('Довгострокові звичайні')
    btn2 = types.KeyboardButton('Середньострокові')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Довгострокові з індексованою вартістю')
    btn2 = types.KeyboardButton('Короткострокові дисконтні')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Довгострокові інфляційні')
    btn2 = types.KeyboardButton('OЗДП')
    markup.row(btn1, btn2)
    btn1 = types.KeyboardButton('Пошук по ISIN')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":house:")} Головне Меню')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, message_text,
                     parse_mode='html', reply_markup=markup)


#########################################################################
# view securities curr menu
#########################################################################
def on_securities_curr_menu_reply(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton('ЦП UAH')
    btn2 = types.KeyboardButton('ЦП USD')
    btn3 = types.KeyboardButton('ЦП EUR')

    if global_securities_type == '6':
        markup.row(btn2, btn3)
    else:
        markup.row(btn1, btn2, btn3)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":left_arrow:")}'
                                f' Назад до вибору типу ЦП')
    markup.row(btn1)
    bot.send_message(message.chat.id,
                     f'{emoji.emojize(":heavy_dollar_sign:")} Виберіть валюту ЦП',
                     parse_mode='html', reply_markup=markup)
    # следующий шаг обработки
    bot.register_next_step_handler(message, on_click_securities_type)


#########################################################################
# view securities curr menu - InlineKeyboardMarkup
#########################################################################
def on_securities_curr_menu_inline(message):
    if global_securities_type == '6':
        markup = types.InlineKeyboardMarkup(keyboard=[
            [
                types.InlineKeyboardButton(text='USD', callback_data='securities_usd'),
                types.InlineKeyboardButton(text='EUR', callback_data='securities_eur'),
            ]
        ], row_width=2)
    else:
        markup = types.InlineKeyboardMarkup(keyboard=[
            [
                types.InlineKeyboardButton(text='UAH', callback_data='securities_uah'),
                types.InlineKeyboardButton(text='USD', callback_data='securities_usd'),
                types.InlineKeyboardButton(text='EUR', callback_data='securities_eur'),
            ]
        ], row_width=3)
    bot.send_message(message.chat.id,
                     f'{emoji.emojize(":heavy_dollar_sign:")} Виберіть валюту ЦП',
                     parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data in ('securities_uah', 'securities_usd', 'securities_eur'):
        p = Read_ISIN_Securities(global_securities_type,
                                 callback.data.upper()[-3:],
                                 "",
                                 False)
        if p.text_error == "":
            if p.text_result == "":
                m_message = ('Цінні папери у ' + callback.data.upper()[-3:] + ' (' +
                             get_name_securities_type(global_securities_type)
                             .replace("%", "") + ') не знайдені.')
                on_securities_menu(callback.message, m_message)
                bot.register_next_step_handler(callback.message, on_click_securities)
            else:
                m_message = p.text_result
                if len(m_message) > 4095:
                    for x in range(0, len(m_message), 4095):
                        on_securities_menu(callback.message, m_message[x:x + 4095])
                else:
                    on_securities_menu(callback.message, m_message)
                # следующий шаг обработки
                bot.register_next_step_handler(callback.message, on_click_securities)
        else:
            bot.send_message(callback.message.chat.id,
                             'Сервіс тимчасово не працює. Спробуйте пізніше.')
            on_click_global(callback.message)
    else:
        # следующий шаг обработки
        bot.register_next_step_handler(callback.message, on_click_securities)


#########################################################################
# securities
#########################################################################
def on_click_securities(message):
    global global_securities_type

    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)

    elif message.text == 'Довгострокові звичайні':
        global_securities_type = '1'
        securities_type(message, 'UAH')

    elif message.text == 'Середньострокові':
        global_securities_type = '4'
        if g_InlineKeyboard:
            on_securities_curr_menu_inline(message)
        else:
            on_securities_curr_menu_reply(message)

    elif message.text == 'Довгострокові з індексованою вартістю':
        global_securities_type = '2'
        securities_type(message, 'UAH')

    elif message.text == 'Короткострокові дисконтні':
        global_securities_type = '5'
        if g_InlineKeyboard:
            on_securities_curr_menu_inline(message)
        else:
            on_securities_curr_menu_reply(message)

    elif message.text == 'Довгострокові інфляційні':
        global_securities_type = '3'
        securities_type(message, 'UAH')

    elif message.text == 'OЗДП':
        global_securities_type = '6'
        if g_InlineKeyboard:
            on_securities_curr_menu_inline(message)
        else:
            on_securities_curr_menu_reply(message)

    elif message.text == 'Пошук по ISIN':
        bot.send_message(message.chat.id, 'Введіть ISIN')
        # следующий шаг обработки
        bot.register_next_step_handler(message, click_securities_others)


#########################################################################
# securities
#########################################################################
def securities_type(message, curr_code):
    p = Read_ISIN_Securities(global_securities_type, curr_code, "", False)
    if p.text_error == "":
        if p.text_result == "":
            m_message = ('Цінні папери ISIN у ' + curr_code
                         + ' (' + message.text + ') не знайдені.')
            on_securities_menu(message, m_message)
            bot.register_next_step_handler(message, on_click_securities)
        else:
            m_message = p.text_result
            if len(m_message) > 4095:
                for x in range(0, len(m_message), 4095):
                    on_securities_menu(message, m_message[x:x + 4095])
            else:
                on_securities_menu(message, m_message)
            # следующий шаг обработки
            bot.register_next_step_handler(message, on_click_securities)
    else:
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)


#########################################################################
# securities
#########################################################################
def on_click_securities_type(message):
    if message.text.endswith('Назад до вибору типу ЦП'):
        on_securities_menu(message,
                           f'{emoji.emojize(":left_arrow:")} Назад до вибору типу ЦП')
        bot.register_next_step_handler(message, on_click_securities)
    elif message.text in ('ЦП UAH', 'ЦП USD', 'ЦП EUR'):
        curr_code = message.text.upper()[-3:]
        message.text = get_name_securities_type(global_securities_type).replace("%", "")
        securities_type(message, curr_code)
    else:
        on_securities_menu(message,
                           f'{emoji.emojize(":left_arrow:")} Назад до вибору типу ЦП')
        bot.register_next_step_handler(message, on_click_securities)


#########################################################################
# securities
#########################################################################
def click_securities_others(message):
    p = Read_ISIN_Securities("", "", message.text.upper().strip(), True)
    if p.text_error == "":
        if p.text_result == "":
            m_message = ('Цінні папери ISIN = ' + message.text.upper().strip()
                         + ' не знайдені.')
            on_securities_menu(message, m_message)
            bot.register_next_step_handler(message, on_click_securities)
        else:
            m_message = p.text_result
            if len(m_message) > 4095:
                for x in range(0, len(m_message), 4095):
                    on_securities_menu(message, m_message[x:x + 4095])
            else:
                on_securities_menu(message, m_message)
            # следующий шаг обработки
            bot.register_next_step_handler(message, on_click_securities)
    else:
        bot.send_message(message.chat.id,
                         'Сервіс тимчасово не працює. Спробуйте пізніше.')
        on_click_global(message)


########################################################
# main
########################################################
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as err:
        time.sleep(10)
        print(err)
