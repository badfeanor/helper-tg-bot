import telebot
import datetime
import requests
import re

from bs4 import BeautifulSoup as bs
from settings import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет ✌️, сегодня " + str(datetime.date.today()) + ". \
    Бот делится с вами курсом валют с сайта ЦБ. Отправьте /currency, чтобы выбрать валюту.")

@bot.message_handler(commands=["currency"])
def currency(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    button_1 = telebot.types.KeyboardButton("Курс Доллара США 💲")
    button_2 = telebot.types.KeyboardButton("Курс Евро 💶")
    button_3 = telebot.types.KeyboardButton("Курс Фунта стерлингов 💷")
    button_4 = telebot.types.KeyboardButton("Курс Белорусского рубля 🇧🇾")
    button_5 = telebot.types.KeyboardButton("Назад")

    markup.add(button_1, button_2, button_3, button_4, button_5)
    bot.send_message(message.chat.id, "Выберите валюту:", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def reply(message):
    match message.text:
        case "Курс Доллара США 💲":
            bot.send_message(message.chat.id, get_currency(actual_currency="Доллар США", date_to_parse=datetime.date.today()))
        case "Курс Евро 💶":
            bot.send_message(message.chat.id, get_currency(actual_currency="Евро", date_to_parse=datetime.date.today()))
        case "Курс Фунта стерлингов 💷":
            bot.send_message(message.chat.id, get_currency(actual_currency="Фунт стерлингов", date_to_parse=datetime.date.today()))
        case "Курс Белорусского рубля 🇧🇾":
            bot.send_message(message.chat.id, get_currency(actual_currency="Белорусский рубль", date_to_parse=datetime.date.today()))
        case "Назад":
            # Закрытие клавиатуры
            bot.send_message(message.chat.id, "Вы закрыли клавиатуру. Отправьте */currency*, чтобы открыть клавиатуру.", reply_markup=types.ReplyKeyboardRemove())
        case _:
            bot.send_message(message.chat.id, "Вы отправили неизвестную мне команду. Отправьте */start* для начала общения с ботом.")

def get_currency(actual_currency: str, date_to_parse) -> str:
    """
    Парсинг курса ЦБ. Если данный курс уже парсился, то данные возьмутся из кэша.
    :param actual_currency: Название валюты.
    :param date_to_parse: Дата курса.
    :return: Текст с именем валюты и её курсом.
    """
    day, month, year = date_to_parse.day, date_to_parse.month, date_to_parse.year
    rate_cache = {}
    compiled_letters_pattern = re.compile(r"[а-яА-я]+")
    compiled_numbers_pattern = re.compile(r"\d+")

    currency = rate_cache.get(f"{day} {month} {year} {actual_currency}")

    if currency:
        return f"Курс *{currency[0]}* на {day}.{month}.{year}: {currency[1]}"

    url = f"https://cbr.ru/scripts/XML_daily.asp?date_req={day}/{month}/{year}"

    request = requests.get(url)
    soup = bs(request.text, "lxml")

    for tag in soup.findAll("valute"):
        result = tag.get_text(strip=True)
        currency_name = " ".join(compiled_letters_pattern.findall(result))
        numbers = compiled_numbers_pattern.findall(result)

        price = f"{numbers[-2]}.{numbers[-1]}"

        if actual_currency in currency_name:
            rate_cache[f"{day} {month} {year} {actual_currency}"] = (currency_name, price)
            return f"Курс *{currency_name}* на {day}.{month}.{year}: {price}"

bot.infinity_polling()