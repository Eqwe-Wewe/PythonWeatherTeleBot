import config
import telebot


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я помогу тебе узнать прогноз погоды.\n' +
        'Чтобы посмотреть данные о погоде на текущий момент ' +
        '/current weather.\n' +
        'Посмотреть прогноз погоды на 10 дней /10 day weather.\n' +
        'Посмотреть прогноз погоды на месяц / month weather.\n' +
        'Выбрать местоположение / location selection.\n' +
        'Получить помощь /help.')


@bot.message_handler(commands=['help'])
def help(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    bot.send_message(
        message.chat.id,
        '1) Для получения прогноза погоды выбери свое местоположение' +
        '/location selection.\n' +
        '2) Посмотреть данные о погоде на текущий момент /current weather.\n' +
        '3) Посмотреть прогноз погоды на 10 дней /10 day weather.\n' +
        '4) Посмотреть прогноз погоды на месяц / month weather.\n' +
        '5) Нажми «Обновить», чтобы получить обновленную информацию о' +
        ' текущей погоде.',
        reply_markup=keyboard)
    keyboard.add(telebot.types.InlineKeyboardButton(
        'Связаться с разработчиком',
        url='telegram.me/developer'))


@bot.message_handler(commands=['current weather'])
def current_weather(message):
    pass


@bot.message_handler(commands=['10 day weather'])
def ten_day_weather(message):
    pass


@bot.message_handler(commands=['month weather'])
def month_weather(message):
    pass


def refresh():
    pass


bot.polling(none_stop=True)
