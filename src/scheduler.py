import telebot
from settings import config
from bot import yandex_weather_new

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")


def function_to_run():
    return bot.send_message(config.CHANNEL_CHAT_ID, yandex_weather_new())


function_to_run()