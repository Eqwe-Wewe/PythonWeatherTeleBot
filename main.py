import config
import requests
from bs4 import BeautifulSoup
import telebot


bot = telebot.TeleBot(config.TOKEN)
url = 'https://yandex.ru/pogoda/'
url_region = 'https://yandex.ru/pogoda/region/225?via=reg'


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
            url='telegram.me/yourrandomdeveloper'))


@bot.message_handler(commands=['current_weather'])
def current_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        get_message(),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current'))


@bot.callback_query_handler(func=lambda call: True)
def weather_callback(query):
    data = query.data
    bot.answer_callback_query(query.id)
    bot.send_chat_action(query.message.chat.id, 'typing')
    if data == 'update_current':
        bot.send_message(
            query.message.chat.id,
            get_message(),
            reply_markup=button(
                text='Обновить',
                callback_data='update_current'))
    elif data == 'update_10_days':
        bot.send_message(
            query.message.chat.id,
            get_message_10_days(),
            reply_markup=button(
                text='Обновить',
                callback_data='update_10_days'))


def button(text: str, url: str = None, callback_data: str = None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text,
            url,
            callback_data))
    return keyboard


def get_message():
    city = parsing(
        'h1',
        'title title_level_1 header-title__title')
    weather_value = parsing(
        'div',
        'term__value')
    return (f'{city[0]}\n'+
            f'текущая температура {"".join([weather_value[0], "C°"])},\n' +
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
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        get_message_10_days(),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days'))


def get_message_10_days():
    city = parsing(
        'h1',
        'title title_level_1 header-title__title')
    ten_day = parsing(
        'div',
        'forecast-briefly__name')
    time = parsing(
        'time',
        'forecast-briefly__date')
    t_day = parsing(
        'div',
        'temp forecast-briefly__temp forecast-briefly__temp_day')
    t_night = parsing(
        'div',
        'temp forecast-briefly__temp forecast-briefly__temp_night')
    condition = parsing(
        'div',
        'forecast-briefly__condition')
    # img = parsing(
    #    'img',
    #    'class="icon icon_thumb_skc-d icon_size_48 icon_color_dark forecast-briefly__icon')
    mes =[', '.join([ten_day[i],
                     time[i],
                     t_day[i],
                     t_night[i],
                     condition[i]])
          + '\n\n'
          for i in range(2, 12)]
    return  (city[0]
             + '\n'
             + 'Прогноз на 10 дней'
             + '\n\n'
             + ''.join(mes))


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    bot.send_chat_action(message.chat.id, 'typing')

    # example
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=5)
    lst=[]
    for i in range(19):
        s = telebot.types.InlineKeyboardButton(
            'Обновить',
            callback_data='update_10_days')
        lst.append(s)
    keyboard.add(*lst)
    print(lst)
    bot.send_message(
        message.chat.id,
        get_location(),
        reply_markup=keyboard)


def get_location():
    html = requests.get(url_region)
    soup = BeautifulSoup(html.text, 'html.parser')
    value = soup(
        'li',
        'place-list__item place-list__item_region_yes')
    names = [name.get_text() for name in value]
    links = ['https://yandex.ru' +
             link.find('a').get('href') for link in value]
    regions = list(zip(names, links)) 
    regions = [': '.join(name) for name in regions]
    return '\n'.join(regions[:20]) # symbols limit is 4096


def gen_row(iterable, num ):
    s=[]
    lst=[]
    #for i in range(len(iterable)):
    for i in range(19):
        s.append(i)
        if len(s) == num:
            lst.append(s)
            s=[]
        elif len(iterable) - (len(lst)*num) < num:
            lst.append([i])
    return lst

'''
def gen_row(iterable, num ):
    s=[]
    lst=[]
    for i in iterable:
        s.append(i)
        if len(s) == num:
            lst.append(s)
            s=[]
        elif len(iterable) - (len(lst)*num) < num:
            lst.append([i])
    return lst'''


bot.polling(none_stop=True)
