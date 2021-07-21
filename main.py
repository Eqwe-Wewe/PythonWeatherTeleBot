import config_tb
from config_db import config
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import telebot
from db import UseDataBase
from emoji import *


# заглавная страница сервиса Яндекс.Погода с прогнозом
# по текущему месту положения
URL = 'https://yandex.ru/pogoda/'

# список регионов России
URL_REGIONS = 'https://yandex.ru/pogoda/region/225?via=reg'

# ссылка на конкретный регион
URL_REGION = None


class Var():
    def __init__(self):

        # первая буква из названия региона
        self.btn = None

        # первая буква из субъекта региона
        self.btn_sub_reg = None

        # список регионов или их субъектов
        self.regions = None


users_property = {}
bot = telebot.TeleBot(config_tb.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    users_property[message.chat.id] = Var()
    with UseDataBase(config) as cursor:
        query = f"""INSERT INTO users_property
                (chat_id, url, url_regions, url_region)
                VALUES ({message.chat.id}, '{URL}',
                '{URL_REGIONS}', '{URL_REGION}')
                ON CONFLICT(chat_id)
                DO NOTHING;"""
        cursor.execute(query)
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

            # по желанию добавьте учетную запись
            url='telegram.me/<yourrandomdeveloper>'))


@bot.message_handler(commands=['current_weather'])
def current_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        # set_message(users_property[message.chat.id].url),
        set_message(get_urls('url', message.chat.id)),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current',
            switch_inline_query='Current'))


@bot.message_handler(commands=['10_day_weather'])
def ten_days_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_message_10_days(get_urls('url', message.chat.id)),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days',
            switch_inline_query='Ten days'))


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    users_property[message.chat.id] = Var()
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = alphabet(
        get_urls(
            'url_regions',
            message.chat.id),
        'set_region_')
    bot.send_message(
        message.chat.id,
        'Выберите первый символ из названия региона РФ',
        reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('update'))
def weather_callback(query):
    data = query.data
    bot.answer_callback_query(query.id)
    if query.message:
        bot.send_chat_action(query.message.chat.id, 'typing')
        if data == 'update_current':
            bot.edit_message_text(
                set_message(
                    get_urls(
                        'url',
                        query.message.chat.id),
                    True),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current',
                    switch_inline_query='Current'))
        elif data == 'update_10_days':
            bot.edit_message_text(
                set_message_10_days(
                    get_urls(
                        'url',
                        query.message.chat.id),
                    True),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_days',
                    switch_inline_query='Ten days'))
    elif query.inline_message_id:
        bot.send_chat_action(query.from_user.id, 'typing')
        if data == 'update_current':
            bot.edit_message_text(
                set_message(
                    get_urls(
                        'url',
                        query.from_user.id),
                    True),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current',
                    switch_inline_query='Current'))
        elif data == 'update_10_days':
            bot.edit_message_text(
                set_message_10_days(
                    get_urls(
                        'url',
                        query.from_user.id),
                    True),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_days',
                    switch_inline_query='Ten days'))


@bot.callback_query_handler(func=lambda call: True)
def location_query(query):
    if query.message.chat.id not in users_property:
        users_property[query.message.chat.id] = Var()
    user = users_property[query.message.chat.id]
    data = query.data
    bot.answer_callback_query(query.id)
    try:
        if data == 'set_location_back':
            keyboard = alphabet(
                get_urls(
                    'url_regions',
                    query.message.chat.id),
                'set_region_')
            bot.edit_message_text(
                'Выберите первый символ из названия региона РФ',
                query.message.chat.id,
                query.message.message_id)
        elif data.startswith('set_region'):
            regions = set_region(
                query.data[-1],
                get_urls(
                    'url_regions',
                    query.message.chat.id))
            keyboard = telebot.types.InlineKeyboardMarkup(2)
            lst = [telebot.types.InlineKeyboardButton(
                regions[region][0],
                callback_data=(f'set_sub_reg{query.data[-1]}' +
                               f'|{regions[region][1]}'))
                   for region in range(len(regions))]
            keyboard.add(*lst)
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='set_location_back'))
            bot.edit_message_text(
                'Выберите регион',
                query.message.chat.id,
                query.message.message_id)
        elif data.startswith('set_sub_reg') or data == 'set_sub_reg_back':
            if data != 'set_sub_reg_back':
                btn, value = query.data.split('|')
                set_urls(
                    'url_region',
                    value,
                    query.message.chat.id)
                user.btn = btn[-1]
            keyboard = alphabet(
                get_urls(
                    'url_region',
                    query.message.chat.id),
                'main_sub_reg')
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data=f'set_region{user.btn}'))
            bot.edit_message_text(
                'Выберите первый символ из названия субъекта региона',
                query.message.chat.id,
                query.message.message_id)
        elif data.startswith('main_sub_reg'):
            if query.data != 'main_sub_reg_back':
                user.btn_sub_reg = query.data[-1]
            url_region = get_urls('url_region', query.message.chat.id)
            user.regions = set_region(user.btn_sub_reg, url_region)
            keyboard = telebot.types.InlineKeyboardMarkup(2)
            lst = [telebot.types.InlineKeyboardButton(
                user.regions[region][0],
                callback_data=f'current|{user.regions[region][0][:12]}')
                for region in range(len(user.regions))]
            keyboard.add(*lst)
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='set_sub_reg_back'))
            bot.edit_message_text(
                'Выберите место',
                query.message.chat.id,
                query.message.message_id)
        elif data.startswith('current'):
            key = query.data.split("|")[1]
            regions = dict(user.regions)
            sub_reg = [(region, regions[region]) for region in regions.keys()
                       if region.startswith(key)]
            set_urls(
                'url',
                sub_reg[0][1],
                query.message.chat.id)
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='main_sub_reg_back'))
            bot.edit_message_text(
                f'Вы выбрали "{sub_reg[0][0]}" локацией по умолчанию.',
                query.message.chat.id,
                query.message.message_id)
    except TypeError:
        keyboard = alphabet(
            get_urls(
                'url_regions',
                query.message.chat.id),
            'set_region_')
        bot.edit_message_text(
            'Выберите первый символ из названия региона РФ',
            query.message.chat.id,
            query.message.message_id)
    bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard)


def set_message(url, change: bool = False):
    sub_reg = parsing(
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
    try:
        wind = get_wind_dir_emoji(weather_value[2].split("м/с, ")[1])
    except IndexError:
        wind = ''
    hour = int((time[0].strip(". ").split(' ')[1].split(':')[0]))
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    return (f'{sub_reg[0]}\n' +
            f'{update}\n' +
            f'{time[0].strip(". ")}(МСК{time_zone(url)})\n' +
            f'текущая температура {"".join([weather_value[0], "°"])}\n' +
            f'ощущается как {"".join([weather_value[1], "°"])}\n' +
            f'{condition[0]} {get_weather_emoji(condition[0], hour)}\n' +
            f'{dashing_away} {weather_value[2]}' +
            f'{wind}\n' +
            f'{droplet} {weather_value[3]} ' +
            f'{barometer} {weather_value[4]}')


def set_message_10_days(url, change: bool = False):
    sub_reg = parsing(
        'h1',
        'title title_level_1 header-title__title',
        url)
    ten_days = parsing(
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
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    mes = [' '.join([ten_days[i],
                     time[i],
                     ('\n' + t_day[i] + '°'),
                     (', ' + t_night[i] + '°')])
           + f'\n {condition[i]}'
           + f' {get_weather_emoji(condition[i].lower())}'
           + '\n\n'
           for i in range(2, 12)]
    return (sub_reg[0]
            + '\nПрогноз на 10 дней\n'
            + f'{update}\n'
            + ''.join(mes))


def set_urls(url, value, chat_id):
    with UseDataBase(config) as cursor:
        operation = f"""UPDATE users_property
                    SET {url} = '{value}'
                    WHERE chat_id = {chat_id};"""
        cursor.execute(operation)


def get_urls(url, chat_id):
    with UseDataBase(config) as cursor:
        operation = f"""SELECT {url} from users_property
                    WHERE chat_id = {chat_id};"""
        cursor.execute(operation)
        result = cursor.fetchall()
    return result[0][0]


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


def set_region(letter, url):
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


def parsing(name: str, attrs: str, url: str):
    value = scraping(name, attrs, url)
    value = [i.get_text() for i in value]
    return value


def scraping(name: str, attrs: str, url: str):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    value = soup.findAll(name, class_=attrs)
    return value


def time_zone(url):
    value = scraping(
        'time',
        'time fact__time',
        url)
    tz = [i.get('datetime') for i in value]
    tz = int(tz[0].split('+')[1][:2]) - 3
    if tz > 0:
        tz = '+' + str(tz)
    elif tz == 0:
        tz = ''
    else:
        tz = '-' + str(tz)
    return tz


def button(text: str, url: str = None, callback_data: str = None,
           switch_inline_query: str = None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    first_btn = telebot.types.InlineKeyboardButton(
        text,
        url,
        callback_data)
    if switch_inline_query:
        keyboard.row(
            first_btn,
            telebot.types.InlineKeyboardButton(
                text='Поделиться',
                switch_inline_query=switch_inline_query))
    else:
        keyboard.add(first_btn)
    return keyboard


def get_weather_emoji(value, hour=None):
    value = value.lower()
    try:
        if hour is not None:

            # яндекс считает ночным временем с 0 ч. по 6 ч.
            if hour < 6:
                return weather_conditions_night[value]
        return weather_conditions[value]
    except KeyError as err:
        with open('report_emoji.txt', 'a') as file:
            print(f'KeyError get_weather_emoji: {err}', file=file)
        return ''


def get_wind_dir_emoji(value):
    return wind_dir[value]


@bot.inline_handler(func=lambda query: True)
def inline_mode(inline_query):
    current = telebot.types.InlineQueryResultArticle(
        '1',
        'Current',
        telebot.types.InputTextMessageContent(
            set_message(
                get_urls(
                    'url',
                    inline_query.from_user.id))),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current',
            switch_inline_query='Current'),
        description='Погода сейчас',
        thumb_url=('https://www.clipartkey.com/mpngs/m/273-2739384_weather' +
                   '-icon-heart.png'))
    ten_days = telebot.types.InlineQueryResultArticle(
        '2',
        'Ten days',
        telebot.types.InputTextMessageContent(
            set_message_10_days(
                get_urls(
                    'url',
                    inline_query.from_user.id))),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days',
            switch_inline_query='Ten days'),
        description='Прогноз на 10 дней',
        thumb_url=('https://unblast.com/wp-content/uploads/2020/05/Weather-' +
                   'Vector-Icons-1536x1152.jpg'))
    bot.answer_inline_query(
        inline_query.id,
        [current, ten_days])


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        dt = datetime.now()
        dt = dt.strftime('%H:%M - %m.%d.%Y')
        with open('report.txt', 'a') as file:
            print(f'error: {err}, {dt}', file=file)
