import config
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import telebot
from emoji import *


class Var():
    def __init__(self):

        # заглавная страница сервиса Яндекс.Погода с прогнозом
        # по текущему месту положения
        self.url = 'https://yandex.ru/pogoda/'

        # список регионов России
        self.url_regions = 'https://yandex.ru/pogoda/region/225?via=reg'

        # ссылка на конкретный регион
        self.url_region = None

        # первая буква из названия региона
        self.btn = None

        # первая буква из субъекта региона
        self.btn_sub_reg = None

        # список регионов или их субъектов
        self.regions = None


users_property = {}
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    user = Var()
    users_property[message.chat.id] = user
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
        set_message(users_property[message.chat.id].url),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current'))


@bot.message_handler(commands=['10_day_weather'])
def ten_days_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_message_10_days(users_property[message.chat.id].url),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days'))


@bot.message_handler(commands=['location_selection'])
def location_selection(message):
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = alphabet(
        users_property[message.chat.id].url_regions,
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
        user = users_property[query.message.chat.id]
        if data == 'update_current':
            bot.edit_message_text(
                set_message(user.url, True),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current'))
        elif data == 'update_10_days':
            bot.edit_message_text(
                set_message_10_days(user.url, True),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_days'))
    elif query.inline_message_id:
        bot.send_chat_action(query.from_user.id, 'typing')
        user = users_property[query.from_user.id]
        if data == 'update_current':
            bot.edit_message_text(
                set_message(user.url, True),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current'))
        elif data == 'update_10_days':
            bot.edit_message_text(
                set_message_10_days(user.url, True),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML')
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_days'))


@bot.callback_query_handler(func=lambda call: True)
def location_query(query):
    user = users_property[query.message.chat.id]
    data = query.data
    bot.answer_callback_query(query.id)
    if data == 'set_location_back':
        keyboard = alphabet(user.url_regions, 'set_region_')
        bot.edit_message_text(
            'Выберите первый символ из названия региона РФ',
            query.message.chat.id,
            query.message.message_id)
    elif data.startswith('set_region'):
        regions = set_region(query.data[-1], user.url_regions)
        keyboard = telebot.types.InlineKeyboardMarkup(2)
        lst = [telebot.types.InlineKeyboardButton(
            regions[region][0],
            callback_data=f'set_sub_reg{query.data[-1]}|{regions[region][1]}')
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
            btn, user.url_region = query.data.split('|')
            user.btn = btn[-1]
        keyboard = alphabet(user.url_region, 'main_sub_reg')
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
        user.regions = set_region(user.btn_sub_reg, user.url_region)
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
        user.url = sub_reg[0][1]
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '<<Назад',
                callback_data='main_sub_reg_back'))
        bot.edit_message_text(
            f'Вы выбрали "{sub_reg[0][0]}" локацией по умолчанию.',
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
            f'{get_wind_dir_emoji(weather_value[2].split("м/с, ")[1])}\n' +
            f'{droplet} {weather_value[3]} ' +
            f'{barometer} {weather_value[4]}')


def set_message_10_days(url, change: bool = False):
    sub_reg = parsing(
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
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    mes = [' '.join([ten_day[i],
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


def button(text: str, url: str = None, callback_data: str = None):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text,
            url,
            callback_data))
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
    user = users_property[inline_query.from_user.id]
    current = telebot.types.InlineQueryResultArticle(
        '1',
        'Погода сейчас',
        telebot.types.InputTextMessageContent(set_message(user.url)),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current'),
        thumb_url=('https://www.clipartkey.com/mpngs/m/273-2739384_weather' +
                   '-icon-heart.png'))
    ten_day = telebot.types.InlineQueryResultArticle(
        '2',
        'Прогноз на 10 дней',
        telebot.types.InputTextMessageContent(set_message_10_days(user.url)),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_days'),
        thumb_url=('https://unblast.com/wp-content/uploads/2020/05/Weather-' +
                   'Vector-Icons-1536x1152.jpg'),
        thumb_width=400,
        thumb_height=400)
    bot.answer_inline_query(
        inline_query.id,
        [current, ten_day])


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
