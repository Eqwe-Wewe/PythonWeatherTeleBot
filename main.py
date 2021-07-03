import config
import requests
from bs4 import BeautifulSoup
import telebot


bot = telebot.TeleBot(config.TOKEN)
url = 'https://yandex.ru/pogoda/'
html = requests.get(url)
soup = BeautifulSoup(html.text, 'html.parser')


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        'Привет! Я помогу тебе узнать прогноз погоды.\n' +
        'Чтобы посмотреть данные о погоде на текущий момент ' +
        '/current_weather.\n' +
        'Посмотреть прогноз погоды на 10 дней /10_day_weather.\n' +
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
        '3) Нажми «Обновить», чтобы получить обновленную информацию о' +
        ' текущей погоде.\n' +
        '4) Для смены региона в прогнозе погоды /location_selection.\n',
        reply_markup=keyboard)


@bot.message_handler(commands=['current_weather'])
def current_weather(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Обновить')
    )
    bot.send_message(
        message.chat.id,
        get_message())


def get_message():
    weather_value = soup.findAll('div', class_="term__value")
    weather_value = [i.get_text() for i in weather_value]
    return (f'Текущая температура {"".join([weather_value[0], "C°"])},\n' +
            f'ощущается как {"".join([weather_value[1], "C°"])}\n' +
            f'ветер {weather_value[2]}\n' +
            f'влажность {weather_value[3]}\n' +
            f'давление {weather_value[4]}')


@bot.message_handler(commands=['10_day_weather'])
def ten_day_weather(message):
    bot.send_message(
        message.chat.id,
        get_message2())


def get_message2():
    ten_day = soup.findAll(
        'div',
        class_='forecast-briefly__day swiper-slide')
    ten_day = [i.get_text() for i in ten_day]
    return (f'{ten_day[0]}\n' +
            f'{ten_day[1]}\n' +
            f'{ten_day[2]}\n' +
            f'{ten_day[3]}')


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    pass


def get_location():
    url = 'https://yandex.ru/pogoda/region/'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    place_list = soup.findAll('div', class_="place-list")
    place_list = [i.get_text() for i in place_list]
    return place_list


def refresh():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
            telebot.types.InlineKeyboardButton(
                    'Обновить данные',
                    current_weather()))


bot.polling(none_stop=True)
