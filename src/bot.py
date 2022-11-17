import telebot
import datetime
from settings import config
from bot_functions import get_currency, yandex_weather_new
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
            bot.send_message(message.chat.id, yandex_weather_new())
            # bot.send_message(message.chat.id, yandex_weather('43.430664','39.931168',config.YANDEX_TOKEN))
        case "Назад":
            # Закрытие клавиатуры
            bot.send_message(message.chat.id, "Вы закрыли клавиатуру. Отправьте */currency*, чтобы открыть клавиатуру.", reply_markup=telebot.types.ReplyKeyboardRemove())
        case _:
            bot.send_message(message.chat.id, "Вы отправили неизвестную мне команду. Отправьте */start* для начала общения с ботом.")

bot.infinity_polling()