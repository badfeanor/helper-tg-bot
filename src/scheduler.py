import telebot
from settings import config
from bot_functions import yandex_weather_new

bot = telebot.TeleBot(config.BOT_NOTIFICATOR_TOKEN, parse_mode="markdown")
bot.send_message(config.CHANNEL_CHAT_ID, yandex_weather_new())
