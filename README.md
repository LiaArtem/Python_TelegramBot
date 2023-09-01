# Python_TelegramBot
Python Telegram Bot (exchange rates, exchange rate conversion, weather, unified register of debtors, security)

IDE - PyCharm Community Edition

Налаштування:
 - Відкрийте Telegram
 - Знайдіть @BotFather і почніть розмову.
 - Надішліть команду /newbot і дотримуйтесь інструкцій.
 - Alright, a new bot. How are we going to call it? Please choose a name for your bot.
   - Вказуємо ім'я: LiaArtemTestBot
 - Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
   - Вказуємо ім'я: LiaArtemTestBot
 - Use this token to access the HTTP API:
   - Отримуємо токен, його використовуватимемо для підключення
   - Зберігаємо токен у файл secret_key.json -> "telegram_key" і кладемо в корінь (формат UTF8)
     {
      "telegram_key": "xxxxxxxx",
      "openweathermap_key": "yyyyyyy"
     }
 - Посилання на бот - t.me/LiaArtemTestBot

У командному рядку терміналу IDE
1) Додаємо бібліотеки
-> pip install pyTelegramBotAPI
-> pip install emoji
-> pip install xmltodict
-> pip install CurrencyConverter

---------------------------------------------------
Оновлення пакетів у IDE PyCharm Community Edition:
-> Settings -> Project:TelegramBot -> Python Interpreter -> Upgrade
