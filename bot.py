import telebot
import datetime
from settings import config

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="markdown")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Привет ✌️, сегодня " + str(datetime.date.today()))

bot.infinity_polling()