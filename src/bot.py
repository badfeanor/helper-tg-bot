import telebot
import datetime
import re
import json
import requests

from bs4 import BeautifulSoup as bs
from settings import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет ✌️, сегодня " + str(datetime.date.today()) + ". \
    Бот делится с вами курсом валют с сайта ЦБ и погодой с Яндекса. Отправь /menu ")

@bot.message_handler(commands=["menu"])
def currency(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    button_1 = telebot.types.KeyboardButton("Курсы валют 📊")
    button_2 = telebot.types.KeyboardButton("Погода в Адлере 🌝")
    button_3 = telebot.types.KeyboardButton("Назад")

    markup.add(button_1, button_2, button_3)
    bot.send_message(message.chat.id, "Выбери кнопку:", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def reply(message):
    match message.text:
        case "Курсы валют 📊":
            bot.send_message(message.chat.id, get_currency(date_to_parse=datetime.date.today()))
        case "Погода в Адлере 🌝":
            bot.send_message(message.chat.id, yandex_weather('43.430664','39.931168',config.YANDEX_TOKEN))
        case "Назад":
            # Закрытие клавиатуры
            bot.send_message(message.chat.id, "Вы закрыли клавиатуру. Отправьте */currency*, чтобы открыть клавиатуру.", reply_markup=types.ReplyKeyboardRemove())
        case _:
            bot.send_message(message.chat.id, "Вы отправили неизвестную мне команду. Отправьте */start* для начала общения с ботом.")

def get_currency(date_to_parse) -> str:
    """
    Парсинг курса ЦБ. Если данный курс уже парсился, то данные возьмутся из кэша.
    :param date_to_parse: Дата курса.
    :return: Текст с именем валюты и её курсом.
    """
    day, month, year = date_to_parse.day, date_to_parse.month, date_to_parse.year
    compiled_letters_pattern = re.compile(r"[а-яА-я]+")
    compiled_numbers_pattern = re.compile(r"\d+")
    valuts = ['Доллар США', 'Евро', 'Белорусский рубль']
    answer = ''
    url = f"https://cbr.ru/scripts/XML_daily.asp?date_req={day}/{month}/{year}"

    request = requests.get(url)
    soup = bs(request.text, "lxml")

    for tag in soup.findAll("valute"):
        result = tag.get_text(strip=True)
        currency_name = " ".join(compiled_letters_pattern.findall(result))
        numbers = compiled_numbers_pattern.findall(result)

        price = f"{numbers[-2]}.{numbers[-1]}"

        if currency_name in valuts:
            answer = answer + str(f"Курс *{currency_name}* на {day}.{month}.{year}: {price}\n")

    return answer

def yandex_weather(latitude, longitude, token_yandex: str):
    url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
    yandex_req = requests.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западный', 'n': 'северный', 'ne': 'северо-восточный', 'e': 'восточный',
                'se': 'юго-восточный', 's': 'южный', 'sw': 'юго-западный', 'w': 'западный', 'с': 'штиль'}

    yandex_json = json.loads(yandex_req.text)
    yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
    for parts in yandex_json['forecast']['parts']:
        parts['condition'] = conditions[parts['condition']]
        parts['wind_dir'] = wind_dir[parts['wind_dir']]

    dict_weather = dict()
    params = ['condition', 'wind_dir', 'wind_speed', 'pressure_mm', 'humidity', 'temp_water']
    for parts in yandex_json['forecast']['parts']:
        dict_weather[parts['part_name']] = dict()
        dict_weather[parts['part_name']]['temp'] = parts['temp_avg']
        for param in params:
            dict_weather[parts['part_name']][param] = parts[param]

    dict_weather['fact'] = dict()
    dict_weather['fact']['temp'] = yandex_json['fact']['temp']
    for param in params:
        dict_weather['fact'][param] = yandex_json['fact'][param]

    dict_weather['link'] = yandex_json['info']['url']

    return (f'Погода в Адлере на сегодня!'
            f' Температура {dict_weather["fact"]["temp"]} градусов.'
            f' А на небе {dict_weather["fact"]["condition"]}.'
            f' Ветер {dict_weather["fact"]["wind_dir"]}, а скорость {dict_weather["fact"]["wind_speed"]} м/с.'
            f' Температура воды {dict_weather["fact"]["temp_water"]} градусов.')

bot.infinity_polling()