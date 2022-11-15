import telebot
import datetime
import re
import json
import requests

from bs4 import BeautifulSoup as bs
from settings import config

import schedule
from threading import Thread
from time import sleep

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")
chatid = config.BOT_TOKEN.split(':')[0]
def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def function_to_run():
    return bot.send_message(chatid, yandex_weather_new())

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
            bot.send_message(message.chat.id, yandex_weather_new())
            # bot.send_message(message.chat.id, yandex_weather('43.430664','39.931168',config.YANDEX_TOKEN))
        case "Назад":
            # Закрытие клавиатуры
            bot.send_message(message.chat.id, "Вы закрыли клавиатуру. Отправьте */currency*, чтобы открыть клавиатуру.", reply_markup=telebot.types.ReplyKeyboardRemove())
        case _:
            bot.send_message(message.chat.id, "Вы отправили неизвестную мне команду. Отправьте */start* для начала общения с ботом.")

def get_currency(date_to_parse) -> str:
    """
    Парсинг курса ЦБ. Если данный курс уже парсился, то данные возьмутся из кэша.
    :param date_to_parse: Дата курса.
    :return: Текст с именем валюты и её курсом.
    """
    year, month, day = str(date_to_parse).split('-')
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

    return (f'Погода в Адлере на сегодня!\n'
            f'Температура *{dict_weather["fact"]["temp"]} градусов*.\n'
            f'На улице *{dict_weather["fact"]["condition"]}*.\n'
            f'Ветер *{dict_weather["fact"]["wind_dir"]}*, а скорость *{dict_weather["fact"]["wind_speed"]} м/с*.\n'
            f'Температура воды {dict_weather["fact"]["temp_water"]} градусов.')

def yandex_weather_new():
    header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'}
    url = "https://yandex.ru/pogoda/?lat=43.52914429&lon=39.98907471"
    htmlContent = requests.get(url, headers=header)
    # with open('test.html', 'w') as output_file:
    #     output_file.write(htmlContent.text)

    soup = bs(htmlContent.text, 'html.parser')

    pogoda_fact = soup.find('div', attrs={'class': 'fact__temp-wrap'}).find('a').get('aria-label')
    print(pogoda_fact)
    pogoda_fact_props_wind = soup.find('div', attrs={'class': 'fact__props'}).find('div', attrs={'class': 'term term_orient_v fact__wind-speed'}).find('span', {'class': 'a11y-hidden'}).get_text()
    print(pogoda_fact_props_wind)
    pogoda_fact_props_humidity = soup.find('div', attrs={'class': 'fact__props'}).find('div', attrs={'class': 'term term_orient_v fact__humidity'}).find('span', {'class': 'a11y-hidden'}).get_text()
    print(pogoda_fact_props_humidity)
    pogoda_fact_props_water = soup.find('div', attrs={'class': 'fact__props'}).find('div', attrs={'class': 'term term_orient_v fact__water'}).find('span', {'class': 'a11y-hidden'}).get_text()
    print(pogoda_fact_props_water)

    pogoda_days = soup.find('div', attrs={'class': 'forecast-briefly__days swiper-container'}).find_all('a')
    pogoda_days_result = ''
    for i, day in enumerate(pogoda_days):
        if 0 < i < 4:
            pogoda_days_result = pogoda_days_result + str(f"{day.get('aria-label')}\n")

    return (f'*Погода в Адлере сейчас!*\n'
            f'{pogoda_fact}\n'
            f'{pogoda_fact_props_wind} {pogoda_fact_props_humidity} {pogoda_fact_props_water}\n\n'
            f'*Прогоз на сегодня и ближайшие пару дней:*\n'
            f'{pogoda_days_result}')


if __name__ == "__main__":
    schedule.every().saturday.at("22:13").do(function_to_run)
    Thread(target=schedule_checker).start()
    bot.infinity_polling()