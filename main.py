import config
import requests
from bs4 import BeautifulSoup
import telebot


bot = telebot.TeleBot(config.TOKEN)
url = 'https://yandex.ru/pogoda/'
url_region = 'https://yandex.ru/pogoda/region/'


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
    bot.send_message(
        message.chat.id,
        '1) Посмотреть данные о погоде на текущий момент /current_weather.\n' +
        '2) Посмотреть прогноз погоды на 10 дней /10_day_weather.\n' +
        '3) Нажми «Обновить», чтобы получить обновленную информацию о' +
        ' погоде.\n' +
        '4) Для смены региона в прогнозе погоды /location_selection.\n',
        reply_markup=button(
            text='Связаться с разработчиком',
            url='telegram.me/developer'))


@bot.message_handler(commands=['current_weather'])
def current_weather(message):
    bot.send_message(
        message.chat.id,
        get_message(),
        reply_markup=button(
            text='Обновить',
            callback_data='update'))


@bot.callback_query_handler(func=lambda call: True)
def weather_callback(query):
    data = query.data
    if data == 'update':
        bot.answer_callback_query(query.id)
        bot.send_chat_action(query.message.chat.id, 'typing')
        bot.send_message(
            query.message.chat.id,
            get_message(),
            reply_markup=button(
                text='Обновить',
                callback_data='update'))


def button(text: str, url: str = None, callback_data: str = None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text,
            url,
            callback_data))
    return keyboard


def get_message():
    weather_value = parsing('div', "term__value")
    return (f'Текущая температура {"".join([weather_value[0], "C°"])},\n' +
            f'ощущается как {"".join([weather_value[1], "C°"])}\n' +
            f'ветер {weather_value[2]}\n' +
            f'влажность {weather_value[3]}\n' +
            f'давление {weather_value[4]}')


def parsing(name: str, attrs: str):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    value = soup.findAll(name, class_=attrs)
    value = [i.get_text() for i in value]
    return value


@bot.message_handler(commands=['10_day_weather'])
def ten_day_weather(message):
    bot.send_message(
        message.chat.id,
        get_message_10_day(),
        reply_markup=button(text='Обновить', callback_data='update'))


def get_message_10_day():
    ten_day = parsing('div', 'forecast-briefly__day swiper-slide')
    return (f'{ten_day[0]}\n' +
            f'{ten_day[1]}\n' +
            f'{ten_day[2]}\n' +
            f'{ten_day[3]}')


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    pass


def get_location():
    html = requests.get(url_region)
    soup = BeautifulSoup(html.text, 'html.parser')
    place_list = soup.findAll('div', class_="place-list")
    place_list = [i.get_text() for i in place_list]
    return place_list


bot.polling(none_stop=True)
