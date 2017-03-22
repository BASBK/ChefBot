import telebot
import config
import menu
import api
import texts
from models import *
import requests
import logging
from flask import Flask

app = Flask(__name__)

bot = telebot.TeleBot(config.token)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
@db_session
def handle_start(message):
    if not User.exists(chatID=message.chat.id):
        User(chatID=message.chat.id, state='start')
    bot.send_message(message.from_user.id, 'Хаюхай!', reply_markup=menu.category_menu())


@bot.message_handler(content_types=['text'])
@db_session
def handle_start(message):
    if message.text in api.get_categories():
        User[message.chat.id].state = message.text
        bot.send_message(message.chat.id, 'А вот и все доставочки, выбирай!', reply_markup=telebot.types.ReplyKeyboardRemove())
        for d in api.get_deliveries(message.text):
            if d['photo_id']:
                bot.send_photo(message.chat.id, d['photo_id'], caption=d['name'], reply_markup=menu.delivery_menu())
            else:
                res = bot.send_photo(message.chat.id, open('tashir.jpg', 'rb'),
                                     caption=d['name'], reply_markup=menu.delivery_menu())
                api.upload_delivery_photo_id(d['name'], res.photo[0].file_id)


@bot.callback_query_handler(func=lambda call: True)
@db_session
def callback_query(call):
    if call.data == 'menu':
        User[call.message.chat.id].state = call.message.caption
        for m in api.get_menu_by_delivery(call.message.caption):
            if m['photo_id']:
                bot.send_photo(call.message.chat.id, m['photo_id'],
                               caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                               reply_markup=menu.buy_menu())
            else:
                res = bot.send_photo(call.message.chat.id, open('pizza.jpg', 'rb'),
                                     caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                                     reply_markup=menu.buy_menu())
                api.upload_menu_photo_id(m['name'], res.photo[0].file_id)
        bot.answer_callback_query(callback_query_id=call.id)
    else:
        menu_name = call.message.caption.split('\n')[0]
        api.add_to_basket(call.message.chat.id, User[call.message.chat.id].state, menu_name, 1)
        bot.answer_callback_query(callback_query_id=call.id)

bot.polling(none_stop=True)
