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
        query = f"""
                    INSERT INTO users_property
                                (
                                chat_id,
                                url,
                                url_region
                                )
                    VALUES      (
                                {message.chat.id},
                                '{URL}',
                                '{URL_REGION}'
                                )
                    ON CONFLICT(chat_id) DO NOTHING;
                """
        cursor.execute(query)
    bot.send_message(
        message.chat.id,
        (
            'Привет! Я помогу тебе узнать прогноз погоды.\n'
            'Чтобы посмотреть данные о погоде на текущий момент '
            '/weather_now.\n'
            'Посмотреть подробный прогноз на сегодня '
            '/weather_today.\n'
            'Посмотреть прогноз погоды на 10 дней /10_day_forecast.\n'
            'Выбрать местоположение /select_city_or_area.\n'
            'Получить помощь /help.\n'
            f'Текущее местоположение: {start_area()}'
        )
    )


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        (
            '1) Посмотреть погоду на текущий момент /weather_now.\n'
            '2) Посмотреть подробный прогноз на сегодня '
            '/weather_today.\n'
            '3) Посмотреть прогноз погоды на 10 дней /10_day_forecast.\n'
            '4) Нажми «Обновить», чтобы получить обновленную информацию о'
            ' погоде.\n'
            '5) Для смены региона в прогнозе погоды /location_selection.\n'
            '6) Бот поддерживает встроенный режим. Введи <yournameforthebot>'
            ' в любом чате и выбери команду для составления прогноза погоды.'
        ),
        # добавьте по желанию
##        reply_markup=button(
##            text='Связаться с разработчиком',
##
##            
##            url='telegram.me/<yourrandomdeveloper>'
##        )
    )


@bot.message_handler(commands=['weather_now'])
def current_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_message(get_urls('url', message.chat.id)),
        parse_mode='html',
        reply_markup=button(
            text='Обновить',
            callback_data='update_current',
            switch_inline_query='Current'
        )
    )


@bot.message_handler(commands=['weather_today'])
def weather_today(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_today_message(get_urls('url', message.chat.id)),
        parse_mode='html',
        reply_markup=button(
            text='Обновить',
            callback_data='update_today',
            switch_inline_query='Today'
        )
    )


@bot.message_handler(commands=['10_day_forecast'])
def ten_day_weather(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        set_message_10_day(get_urls('url', message.chat.id)),
        parse_mode='html',
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_day',
            switch_inline_query='10 day'
        )
    )


def start_area():
    soup = scraping(URL)
    area = soup.find('ol', 'breadcrumbs__list')
    country, region, area = area.find_all('span', 'breadcrumbs__title')
    return f'{country.text}  > {region.text} > {area.text}'


@bot.message_handler(commands=['select_city_or_area'])
def location_selection(message):
    users_property[message.chat.id] = Var()
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = alphabet(
        URL_REGIONS,
        'set_region'
    )
    bot.send_message(
        message.chat.id,
        'Выберите первый символ из названия региона РФ',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('update'))
def weather_callback(query):
    bot.answer_callback_query(query.id)
    if query.message:
        bot.send_chat_action(query.message.chat.id, 'typing')
        if query.data == 'update_current':
            bot.edit_message_text(
                set_message(
                    get_urls(
                        'url',
                        query.message.chat.id
                    ),
                    True
                ),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current',
                    switch_inline_query='Current'
                )
            )
        elif query.data == 'update_10_day':
            bot.edit_message_text(
                set_message_10_day(
                    get_urls(
                        'url',
                        query.message.chat.id
                    ),
                    True
                ),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_day',
                    switch_inline_query='10 day'
                )
            )
        elif query.data == 'update_today':
            bot.edit_message_text(
                set_today_message(
                    get_urls(
                        'url',
                        query.message.chat.id
                    ),
                    True
                ),
                query.message.chat.id,
                query.message.message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                query.message.chat.id,
                query.message.message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_today',
                    switch_inline_query='Today'
                )
            )
    elif query.inline_message_id:
        bot.send_chat_action(query.from_user.id, 'typing')
        if query.data == 'update_current':
            bot.edit_message_text(
                set_message(
                    get_urls(
                        'url',
                        query.from_user.id
                    ),
                    True
                ),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_current',
                    switch_inline_query='Current'
                )
            )
        elif query.data == 'update_10_day':
            bot.edit_message_text(
                set_message_10_day(
                    get_urls(
                        'url',
                        query.from_user.id
                    ),
                    True
                ),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_10_day',
                    switch_inline_query='10 day'
                )
            )
        elif query.data == 'update_today':
            bot.edit_message_text(
                set_today_message(
                    get_urls(
                        'url',
                        query.from_user.id
                    ),
                    True
                ),
                inline_message_id=query.inline_message_id,
                parse_mode='HTML'
            )
            bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=button(
                    text='Обновить',
                    callback_data='update_today',
                    switch_inline_query='Today'
                )
            )


@bot.callback_query_handler(func=lambda call: True)
def location_query(query):
    if query.message.chat.id not in users_property:
        users_property[query.message.chat.id] = Var()
    user = users_property[query.message.chat.id]
    bot.answer_callback_query(query.id)
    try:
        if query.data == 'set_location_back':
            keyboard = alphabet(
                URL_REGIONS,
                'set_region'
            )
            bot.edit_message_text(
                'Выберите первый символ из названия региона РФ',
                query.message.chat.id,
                query.message.message_id
            )
        elif query.data.startswith('set_region'):
            regions = set_region(
                query.data[-1],
                URL_REGIONS
            )
            keyboard = telebot.types.InlineKeyboardMarkup(2)
            lst = [
                telebot.types.InlineKeyboardButton(
                    regions[region][0],
                    callback_data=(
                        f'set_sub_reg{query.data[-1]}'
                        f'|{regions[region][1]}'
                    )
                )
                for region in range(len(regions))
            ]
            keyboard.add(*lst)
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='set_location_back'
                )
            )
            bot.edit_message_text(
                'Выберите регион',
                query.message.chat.id,
                query.message.message_id
            )
        elif (query.data.startswith('set_sub_reg')
              or query.data == 'set_sub_reg_back'):
            if query.data != 'set_sub_reg_back':
                btn, value = query.data.split('|')
                set_urls(
                    'url_region',
                    value,
                    query.message.chat.id
                )
                user.btn = btn[-1]
            keyboard = alphabet(
                get_urls(
                    'url_region',
                    query.message.chat.id
                ),
                'main_sub_reg'
            )
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data=f'set_region{user.btn}'
                )
            )
            bot.edit_message_text(
                'Выберите первый символ из названия субъекта региона',
                query.message.chat.id,
                query.message.message_id
            )
        elif query.data.startswith('main_sub_reg'):
            if query.data != 'main_sub_reg_back':
                user.btn_sub_reg = query.data[-1]
            url_region = get_urls('url_region', query.message.chat.id)
            user.regions = set_region(user.btn_sub_reg, url_region)
            keyboard = telebot.types.InlineKeyboardMarkup(2)
            lst = [
                telebot.types.InlineKeyboardButton(
                    user.regions[region][0],
                    callback_data=f'current|{user.regions[region][0][:12]}'
                )
                for region in range(len(user.regions))
            ]
            keyboard.add(*lst)
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='set_sub_reg_back'
                )
            )
            bot.edit_message_text(
                'Выберите место',
                query.message.chat.id,
                query.message.message_id
            )
        elif query.data.startswith('current'):
            key = query.data.split("|")[1]
            regions = dict(user.regions)
            sub_reg = [
                (region, regions[region]) for region in regions.keys()
                if region.startswith(key)
            ]
            set_urls(
                'url',
                sub_reg[0][1],
                query.message.chat.id
            )
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    '<<Назад',
                    callback_data='main_sub_reg_back'
                )
            )
            bot.edit_message_text(
                f'Вы выбрали "{sub_reg[0][0]}" локацией по умолчанию.',
                query.message.chat.id,
                query.message.message_id
            )
    except TypeError:
        keyboard = alphabet(
            URL_REGIONS,
            'set_region'
        )
        bot.edit_message_text(
            'Выберите первый символ из названия региона РФ',
            query.message.chat.id,
            query.message.message_id
        )
    bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard
    )


def scraping(url: str):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')
    return soup


def set_message(url, change: bool = False):
    soup = scraping(url)
    sub_reg = soup.find('h1').text
    area = soup.find('ol', 'breadcrumbs__list')
    region = area.find_all('span', 'breadcrumbs__title')[1].text
    weather_value = soup.find_all('div', 'term__value')
    condition = soup.find('div', 'link__condition day-anchor i-bem').text
    time = soup.find('time')
    current_time = time.text
    tz = time.get('datetime')
    time_of_day = int((tz.strip(". ").split(' ')[1].split(':')[0]))
    weather_value = [item.text for item in weather_value]
    try:
        wind = wind_dir[(weather_value[2].split("м/с, ")[1])]
    except IndexError:
        wind = ''
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    sun_card = soup.find('div', 'sun-card__text-info')
    for v, item in enumerate(sun_card):
        if v == 2:
            magnetic_field = item
        elif v == 4:
            uv_index = item
    return (
        f'{sub_reg}\n(<i>{region}</i>)\n'
        f'{update}\n'
        f'{current_time.strip(". ")}(МСК{time_zone(tz)})\n'
        f'текущая температура {"".join([weather_value[0], "°"])}\n'
        f'ощущается как {"".join([weather_value[1], "°"])}\n'
        f'{condition} {get_weather_emoji(condition, time_of_day)}\n'
        f'{dashing_away} {weather_value[2]}'
        f'{wind}\n'
        f'{droplet} {weather_value[3]} '
        f'{barometer} {weather_value[4]}\n'
        f'{uv_index}\n'
        f'{magnetic_field}'
    )


def set_today_message(url, change=None):
    url = url.split('?')[0] + '/details'
    soup = scraping(url)
    area = soup.find('nav', 'breadcrumbs')
    region, city = area.find_all('span', 'breadcrumbs__title')[1:3]
    data = soup.find('div', 'card')
    fields_val = soup.find_all('dd', 'forecast-fields__value')[:2]
    uv_index, magnetic_field = [item.text for item in fields_val]
    today = data.find(
        'h2',
        'forecast-details__title'
    )
    day = today.find('strong').text
    month = today.find('span').text
    table = data.find_all(
        'tr',
        'weather-table__row'
    )
    rows = []
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    for val in table:
        daypart = val.find(
            'div',
            'weather-table__daypart'
        ).text

        # температура, прогнозируемая на определенную часть суток
        # и как она ощущается
        temp = val.find_all(
            'span',
            'temp__value temp__value_with-unit'
        )
        temp = [t.text for t in temp]
        condition = val.find(
            'td',
            'weather-table__body-cell weather-table__body-cell_type_condition'
        ).text
        pressure = val.find(
            'td',
            (
                'weather-table__body-cell weather-table__body-cell_type_air-'
                'pressure'
            )
        ).text
        humidity = val.find(
            'td',
            'weather-table__body-cell weather-table__body-cell_type_humidity'
        ).text
        wind_speed = val.find('span', 'wind-speed').text
        direct = val.find('abbr').text
        rows.append(
            {
                'daypart': daypart,
                'temp': temp,
                'condition': condition,
                'pressure': pressure,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'direct': direct
            }
        )
    mes = [
        ' '.join
        (
            [
                i["daypart"].capitalize(),
                (
                    i["temp"][0] +
                    '°' +
                    '...' +
                    i["temp"][1] +
                    '°'
                ),
                '\n',
                i["condition"],
                get_weather_emoji(
                    i["condition"],
                    i["daypart"]
                ),
                '\n',
                barometer,
                i["pressure"],
                droplet,
                i["humidity"],
                dashing_away,
                i["wind_speed"],
                i["direct"],
                wind_dir[i["direct"]],
                '\n',
                'ощущается как',
                (i["temp"][2] +
                 '°'),
                '\n\n'
            ]
        )
        for i in rows
    ]
    return (
        f'Cегодня {day} {month}\n'
        f'{city.text}\n<i>({region.text})</i>\n'
        f'{update}\n'
        f'{"".join(mes)}'
        f'УФ-индекс {uv_index}\n'
        f'Магнитное поле {magnetic_field}'
    )


def set_message_10_day(url, change: bool = False):
    soup = scraping(url)
    sub_reg = soup.find(
        'h1',
        class_='title title_level_1 header-title__title'
    ).text
    area = soup.find('ol', 'breadcrumbs__list')
    region = area.find_all('span', 'breadcrumbs__title')[1].text
    ten_day = soup.find_all('div', 'forecast-briefly__name')
    time = soup.find_all('time', class_='forecast-briefly__date')
    t_day = soup.find_all(
        'div',
        class_='temp forecast-briefly__temp forecast-briefly__temp_day'
    )
    t_night = soup.find_all(
        'div',
        class_='temp forecast-briefly__temp forecast-briefly__temp_night'
    )
    condition = soup.find_all('div', class_='forecast-briefly__condition')
    if change is True:
        update = '<i>(Обновлено)</i>\n'
    else:
        update = ''
    mes = [
        ' '.join(
            [
                ten_day[i].text,
                time[i].text,
                (
                    '\n'
                    + t_day[i].text
                    + '°'
                ),
                (
                    ', '
                    + t_night[i].text
                    + '°'
                )
            ]
        )
        + f'\n {condition[i].text}'
        + f' {get_weather_emoji(condition[i].text)}'
        + '\n\n'
        for i in range(2, 12)
    ]
    return (
        f'{sub_reg}'
        f'\n<i>({region})</i>'
        '\nПрогноз на 10 дней\n'
        f'{update}\n'
        f'{"".join(mes)}'
    )


def set_urls(url, value, chat_id):
    with UseDataBase(config) as cursor:
        operation = f"""
                        UPDATE users_property
                        SET    {url} = '{value}'
                        WHERE  chat_id = {chat_id};
                    """
        cursor.execute(operation)


def get_urls(url, chat_id):
    with UseDataBase(config) as cursor:
        operation = f"""
                        SELECT {url}
                        FROM   users_property
                        WHERE  chat_id = {chat_id};
                    """
        cursor.execute(operation)
        result = cursor.fetchall()
    return result[0][0]


def alphabet(url, choosing_region):
    alphabet = scraping(url)
    alphabet = alphabet.find_all(
        'h2',
        'title title_level_2 place-list__letter'
    )
    alphabet = [i.get_text() for i in alphabet]
    keyboard = keyboard_rows(alphabet, choosing_region)
    return keyboard


def keyboard_rows(data, choosing_region):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
    lst = [
        telebot.types.InlineKeyboardButton(
            data[btn],
            callback_data=f'{choosing_region + data[btn]}'
        )
        for btn in range(len(data))
    ]
    keyboard.add(*lst)
    return keyboard


def set_region(letter, url):
    regions = get_location(url)
    regions = [
        (region, regions[region]) for region in regions.keys()
        if region.startswith(letter)
    ]
    return regions


def get_location(url):
    soup = scraping(url)
    soup = soup.find_all(
        'li',
        'place-list__item place-list__item_region_yes'
    )
    names = [name.get_text() for name in soup]
    links = [
        'https://yandex.ru' +
        link.find('a').get('href') for link in soup
    ]
    regions = dict(zip(names, links))
    return regions


def time_zone(tz):
    tz = int(tz.split('+')[1][:2]) - 3
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
        callback_data
    )
    if switch_inline_query:
        keyboard.row(
            first_btn,
            telebot.types.InlineKeyboardButton(
                text='Поделиться',
                switch_inline_query=switch_inline_query
            )
        )
    else:
        keyboard.add(first_btn)
    return keyboard


def get_weather_emoji(value, hour=None):
    value = value.lower()
    try:
        if hour is not None:

            # яндекс считает ночным временем с 0 ч. по 6 ч.
            if isinstance(hour, str):
                if hour == 'ночью':
                    hour = 3  # для удобства получения emoji выбрано это время
            if isinstance(hour, int):
                if hour < 6:
                    return weather_conditions_night[value]
        return weather_conditions[value]
    except KeyError as err:
        with open('report_emoji.txt', 'a') as file:
            print(f'KeyError get_weather_emoji: {err}', file=file)
        return ''


@bot.inline_handler(func=lambda query: True)
def inline_mode(inline_query):
    current = telebot.types.InlineQueryResultArticle(
        '1',
        'Current',
        telebot.types.InputTextMessageContent(
            set_message(
                get_urls(
                    'url',
                    inline_query.from_user.id
                )
            )
        ),
        reply_markup=button(
            text='Обновить',
            callback_data='update_current',
            switch_inline_query='Current'
        ),
        description='Погода сейчас',
        thumb_url=(
            'https://www.clipartkey.com/mpngs/m/273-2739384_weather'
            '-icon-heart.png'
        )
    )
    ten_day = telebot.types.InlineQueryResultArticle(
        '3',
        '10 day',
        telebot.types.InputTextMessageContent(
            set_message_10_day(
                get_urls(
                    'url',
                    inline_query.from_user.id
                )
            )
        ),
        reply_markup=button(
            text='Обновить',
            callback_data='update_10_day',
            switch_inline_query='10 day'
        ),
        description='Прогноз на 10 дней',
        thumb_url=(
            'https://unblast.com/wp-content/uploads/2020/05/Weather-'
            'Vector-Icons-1536x1152.jpg'
        )
    )
    today = telebot.types.InlineQueryResultArticle(
        '2',
        'Today',
        telebot.types.InputTextMessageContent(
            set_today_message(
                get_urls(
                    'url',
                    inline_query.from_user.id
                )
            )
        ),
        reply_markup=button(
            text='Обновить',
            callback_data='update_today',
            switch_inline_query='Today'
        ),
        description='Прогноз на сегодня',
        thumb_url=(
            'https://www.clipartkey.com/mpngs/m/273-2739384_weather'
            '-icon-heart.png'
        )
    )
    bot.answer_inline_query(
        inline_query.id,
        [current, today, ten_day]
    )


if __name__ == '__main__':
    bot.polling(none_stop=True)
