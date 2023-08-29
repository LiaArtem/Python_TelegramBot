import time
import telebot
from telebot import types
import emoji  # https://carpedm20.github.io/emoji/
from datetime import date
from curs import Read_curs
from convert_curs import Read_convert_curs

# read token to access the HTTP API
token_key = open(file='token.txt', mode="r", encoding="utf8").read()
bot = telebot.TeleBot(token_key)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Головне Меню"),
    telebot.types.BotCommand("/curs", "Курси валют"),
    telebot.types.BotCommand("/convert_curs", "Конвертер валют")
])

# global variables
global_convert_code_from = ''
global_convert_code_to = ''


#########################################################################
# commands=['start']
#########################################################################
@bot.message_handler(commands=['start'])
def start(message):
    message_text = (f'Привіт {emoji.emojize(":grinning_face:")} <b>{message.from_user.first_name} '
                    f'{message.from_user.last_name}</b> обери пункт з головного меню.')
    on_global_menu(message, message_text)
    bot.register_next_step_handler(message, on_click_start)  # следующий шаг обработка гравного меню


#########################################################################
# commands=['curs']
#########################################################################
@bot.message_handler(commands=['curs'])
def curs(message):
    on_click_start(message)


#########################################################################
# commands=['convert_curs']
#########################################################################
@bot.message_handler(commands=['convert_curs'])
def convert_curs(message):
    on_click_start(message)


#########################################################################
# global menu
#########################################################################
def on_global_menu(message, message_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":money_bag:")} Курси валют')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":currency_exchange:")} Конвертер валют')
    markup.add(btn1, btn2)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":rolled-up_newspaper:")} Цінні папери')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":check_box_with_check:")} Запроси у ЄРБ')
    markup.add(btn1, btn2)
    btn1 = types.KeyboardButton(f'{emoji.emojize(":sun_behind_small_cloud:")} Погода')
    btn2 = types.KeyboardButton(f'{emoji.emojize(":credit_card:")} Меню оплати')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, message_text, parse_mode='html', reply_markup=markup)


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
    if message.text.endswith('Курси валют') or message.text == "/curs":
        # выводим новое меню по курсам валют
        on_curs_menu(message, f'{emoji.emojize(":heavy_dollar_sign:")} Оберіть валюту')
        bot.register_next_step_handler(message, on_click_curs)  # следующий шаг обработка курсов

    elif message.text.endswith('Конвертер валют') or message.text == "/convert_curs":
        # убираем главное окно
        # выводим новое меню по конвертеру валют
        on_convert_curs_menu(message, f'{emoji.emojize(":heavy_dollar_sign:")} Оберіть валюти')
        bot.register_next_step_handler(message, on_click_convert_curs)  # следующий шаг обработка конвертации курсов

    else:
        bot.register_next_step_handler(message, on_click_start)  # следующий шаг обработки


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
    bot.send_message(message.chat.id, message_text, parse_mode='html', reply_markup=markup)


#########################################################################
# curs
#########################################################################
def on_click_curs(message):
    if message.text.endswith('Головне Меню'):
        # Возврат в главное меню
        on_click_global(message)
    elif message.text in ('USD - Долар США', 'EUR - ЄВРО', 'GBP - Фунт стерлінгів', 'PLN - Польский злотий'):
        p = Read_curs(date.today(), message.text.upper()[0:3])
        if p.is_request_curs:
            bot.send_message(message.chat.id, 'Курс ' + message.text.upper()[0:3] + ' не найден')
        else:
            m_message = ('Курс ' + message.text.upper()[0:3] + ' (' + p.curr_name + ')' +
                         " = {:.2f}".format(p.curs_amount) + ' грн.')
            # вызов меню курсов для повторного выбора
            on_curs_menu(message, m_message)
            bot.register_next_step_handler(message, on_click_curs)  # следующий шаг обработка курсов

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
        bot.register_next_step_handler(message, on_click_curs)  # следующий шаг обработка курсов


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
    bot.send_message(message.chat.id, message_text, parse_mode='html', reply_markup=markup)


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
        bot.send_message(message.chat.id, 'Введіть коди валют для конвертації (наприклад USD/EUR)')
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
            m_message = 'Конвертація пройшла з помилкою, можливо введені неправильні коди валют'
            on_convert_curs_menu(message, m_message)
            bot.register_next_step_handler(message, on_click_convert_curs)  # следующий шаг обработки
            return

        m_message = ("{:.2f}".format(amount) + ' ' + global_convert_code_from + ' = '
                     + "{:.2f}".format(cc.curs_amount) + ' ' + global_convert_code_to)
        on_convert_curs_menu(message, m_message)
        bot.register_next_step_handler(message, on_click_convert_curs)  # следующий шаг обработки
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
    except Exception:
        bot.send_message(message.chat.id, 'Введені некорректні коди валют для конвертації (наприклад USD/EUR)')
        bot.register_next_step_handler(message, click_convert_curs_others)


########################################################
# main
########################################################
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as err:
        time.sleep(10)
        print(err)
