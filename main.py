import telebot
import config
import menu
import api
import texts
from flask import Flask

app = Flask(__name__)

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.from_user.id, 'Хаюхай!', reply_markup=menu.category_menu())


@bot.message_handler(content_types=['text'])
def handle_start(message):
    if message.text == 'Пиццерия':
        for d in api.get_deliveries(message.text):
            bot.send_message(message.from_user.id, d, reply_markup=menu.delivery_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'menu':
        bot.answer_callback_query(callback_query_id=call.id)
        for m in api.get_menu(call.message.text):
            bot.send_message(call.message.chat.id, texts.menuItem.format(m['name'], m['description'],
                                                                         m['weight'], m['price']))
            

bot.polling(none_stop=True)