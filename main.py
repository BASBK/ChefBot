import telebot
import config
from flask import Flask

app = Flask(__name__)

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.from_user.id, 'Хаюхай!', reply_markup=config.start_menu())

bot.polling(none_stop=True)