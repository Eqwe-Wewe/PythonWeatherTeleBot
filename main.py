import config
import requests
from bs4 import BeautifulSoup
import telebot


class Var():
    # заглавная страница сервиса Яндекс.Погода с прогнозом по текущему месту
    # положения
    url = 'https://yandex.ru/pogoda/'

    # список регионов
    url_region = 'https://yandex.ru/pogoda/region/225?via=reg'

    # первая буква из названия региона
    btn = None


bot = telebot.TeleBot(config.TOKEN)


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
        set_message(Var.url),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current'))


@bot.message_handler(commands=['10_day_weather'])
def ten_day_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_message_10_days(Var.url),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days'))


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = alphabet(Var.url_region, 'set_region_')
    bot.send_message(
        message.chat.id,
        'Выберите первый символ из названия региона РФ',
        reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def weather_callback(query):
    data = query.data
    bot.answer_callback_query(query.id)
    bot.send_chat_action(query.message.chat.id, 'typing')
    if data == 'update_current':
        bot.send_message(
            query.message.chat.id,
            set_message(Var.url),
            reply_markup=button(
                text='Обновить',
                callback_data='update_current'))
    elif data == 'update_10_days':
        bot.send_message(
            query.message.chat.id,
            set_message_10_days(Var.url),
            reply_markup=button(
                text='Обновить',
                callback_data='update_10_days'))
    elif data == 'set_location_back':
        keyboard = alphabet(Var.url_region, 'set_region_')
        bot.send_message(
            query.message.chat.id,
            'Выберите первый символ из названия региона РФ',
            reply_markup=keyboard)
    elif data.startswith('set_region'):
        regions = set_region(query.data[-1], Var.url_region)
        keyboard = telebot.types.InlineKeyboardMarkup(2)
        lst = [telebot.types.InlineKeyboardButton(
            regions[region][0],
            callback_data=f'set_city{query.data[-1]}|{regions[region][1]}')
               for region in range(len(regions))]
        keyboard.add(*lst)
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                '<<Назад',
                callback_data='set_location_back'))
        bot.send_message(
            query.message.chat.id,
            'Выберите регион',
            reply_markup=keyboard)
    elif data.startswith('set_city') or data == 'set_city_back':
        if data != 'set_city_back':
            btn, Var.url_city = query.data.split('|')
            Var.btn = btn[-1]
        keyboard = alphabet(Var.url_city, 'main_city')
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                '<<Назад',
                callback_data=f'set_region{Var.btn}'))
        bot.send_message(
            query.message.chat.id,
            'Выберите первый символ из названия субъекта региона',
            reply_markup=keyboard)
    elif data.startswith('main_city'):
        Var.regions = set_region(query.data[-1], Var.url_city)
        keyboard = telebot.types.InlineKeyboardMarkup(2)
        lst = [telebot.types.InlineKeyboardButton(
            Var.regions[region][0],
            callback_data=f'current|{Var.regions[region][0][:12]}')
               for region in range(len(Var.regions))]
        keyboard.add(*lst)
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                '<<Назад',
                callback_data='set_city_back'))
        bot.send_message(
            query.message.chat.id,
            text='Выберите место',
            reply_markup=keyboard)
    elif data.startswith('current'):
        key = query.data.split("|")[1]
        regions = dict(Var.regions)
        city = [(region, regions[region]) for region in regions.keys()
                if region.startswith(key)]
        Var.url = city[0][1]
        bot.send_message(
            query.message.chat.id,
            f'Вы выбрали "{city[0][0]}" локацией по умолчанию.')


def set_message(url):
    city = parsing(
        'h1',
        'title title_level_1 header-title__title',
        url)
    time = parsing(
        'time',
        'time fact__time',
        url)
    weather_value = parsing(
        'div',
        'term__value',
        url)
    condition = parsing(
        'div',
        'link__condition day-anchor i-bem',
        url)
    return (f'{city[0]} \n' +
            f'{time[0].strip(". ")} по местному времени(МСК{time_zone()})\n' +
            f'текущая температура {"".join([weather_value[0], "C°"])}\n' +
            f'ощущается как {"".join([weather_value[1], "C°"])}\n' +
            f'{condition[0].lower()}\n' +
            f'ветер {weather_value[2]}\n' +
            f'влажность {weather_value[3]}\n' +
            f'давление {weather_value[4]}')


def set_message_10_days(url):
    city = parsing(
        'h1',
        'title title_level_1 header-title__title',
        url)
    ten_day = parsing(
        'div',
        'forecast-briefly__name',
        url)
    time = parsing(
        'time',
        'forecast-briefly__date',
        url)
    t_day = parsing(
        'div',
        'temp forecast-briefly__temp forecast-briefly__temp_day',
        url)
    t_night = parsing(
        'div',
        'temp forecast-briefly__temp forecast-briefly__temp_night',
        url)
    condition = parsing(
        'div',
        'forecast-briefly__condition',
        url)
    mes = [', '.join([ten_day[i],
                      time[i],
                      t_day[i],
                      t_night[i],
                      condition[i]])
           + '\n\n'
           for i in range(2, 12)]
    return (city[0]
            + '\n'
            + 'Прогноз на 10 дней'
            + '\n\n'
            + ''.join(mes))


def alphabet(url, choosing_region):
    alphabet = parsing(
        'h2',
        'title title_level_2 place-list__letter',
        url)
    keyboard = keyboard_rows(alphabet, choosing_region)
    return keyboard


def keyboard_rows(data, choosing_region):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
    lst = [telebot.types.InlineKeyboardButton(
            data[btn],
            callback_data=f'{choosing_region + data[btn]}')
           for btn in range(len(data))]
    keyboard.add(*lst)
    return keyboard


def set_region(letter, url=Var.url_region):
    regions = get_location(url)
    regions = [(region, regions[region]) for region in regions.keys()
               if region.startswith(letter)]
    return regions


def get_location(url):
    value = scraping(
        'li',
        'place-list__item place-list__item_region_yes',
        url)
    names = [name.get_text() for name in value]
    links = ['https://yandex.ru' +
             link.find('a').get('href') for link in value]
    regions = dict(zip(names, links))
    return regions


def parsing(name: str, attrs: str, url: str = Var.url_region):
    value = scraping(name, attrs, url)
    value = [i.get_text() for i in value]
    return value


def scraping(name: str, attrs: str, url: str = Var.url_region):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    value = soup.findAll(name, class_=attrs)
    return value


def time_zone():
    value = scraping(
        'time',
        'time fact__time',
        Var.url)
    tz = [i.get('datetime') for i in value]
    tz = int(tz[0].split('+')[1][:2]) - 3
    if tz > 0:
        tz = '+' + str(tz)
    elif tz == 0:
        tz = ''
    else:
        tz = '-' + str(tz)
    return tz


def button(text: str, url: str = None, callback_data: str = None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text,
            url,
            callback_data))
    return keyboard


bot.polling(none_stop=True)
