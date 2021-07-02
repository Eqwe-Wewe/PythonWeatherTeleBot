import config
import requests
from bs4 import BeautifulSoup
import telebot


bot = telebot.TeleBot(config.TOKEN)
url = 'https://yandex.ru/pogoda/'


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я помогу тебе узнать прогноз погоды.\n' +
        'Чтобы посмотреть данные о погоде на текущий момент ' +
        '/current_weather.\n' +
        'Посмотреть прогноз погоды на 10 дней /10_day_weather.\n' +
        'Посмотреть прогноз погоды на месяц /month_weather.\n' +
        'Выбрать местоположение /location_selection.\n' +
        'Получить помощь /help.')


@bot.message_handler(commands=['help'])
def help(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(
        'Связаться с разработчиком',
        url='telegram.me/developer'))
    bot.send_message(
        message.chat.id,
        '1) Посмотреть данные о погоде на текущий момент /current_weather.\n' +
        '2) Посмотреть прогноз погоды на 10 дней /10_day_weather.\n' +
        '3) Посмотреть прогноз погоды на месяц /month_weather.\n' +
        '4) Нажми «Обновить», чтобы получить обновленную информацию о' +
        ' текущей погоде.',
        '5) Для смены местоположения прогноза погоды /location_selection.\n',
        reply_markup=keyboard)


@bot.message_handler(commands=['current_weather'])
def current_weather(message):
    bot.send_message(
        message.chat.id,
        get_message())


def get_message():
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    return soup.get_text()


@bot.message_handler(commands=['10_day_weather'])
def ten_day_weather(message):
    pass


@bot.message_handler(commands=['month_weather'])
def month_weather(message):
    pass


def refresh():
    current_weather()


bot.polling(none_stop=True)
