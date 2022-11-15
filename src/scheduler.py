import telebot
from settings import config
from bot import yandex_weather_new

import schedule
import time

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")

def function_to_run():
    return bot.send_message(config.CHANNEL_CHAT_ID, yandex_weather_new())


schedule.every().day.at("21:12").do(function_to_run())

while True:
    schedule.run_pending()
    time.sleep(1)
