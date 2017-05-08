import telebot
import config
import menu
import api
import texts
from models import *
import requests
import logging
from PIL import Image
from urllib.request import urlopen
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
def handle_text(message):
    if message.text in api.get_categories():
        User[message.chat.id].state = message.text
        bot.send_message(message.chat.id, 'А вот и все доставочки, выбирай!', reply_markup=telebot.types.ReplyKeyboardRemove())
        for d in api.get_deliveries(message.text):
            if d['photo_id']:
                bot.send_photo(message.chat.id, d['photo_id'], caption=d['name'], reply_markup=menu.delivery_menu())
            else:
                # img = Image.open(urlopen(config.baseImgURL + d['photo']))
                res = bot.send_photo(message.chat.id, urlopen(config.baseImgURL + d['photo']).read(),
                                     caption=d['name'], reply_markup=menu.delivery_menu())
                api.upload_delivery_photo_id(d['name'], res.photo[0].file_id)
    elif message.text == 'Корзина':
        number = 0
        total_price = 0
        cart_text = 'В Вашей корзине:\n'
        for item in api.get_cart(message.from_user.username):
            number += 1
            cart_text += texts.cartItem.format(str(number), item['menu_position'], item['price'], item['count'])
            total_price += item['price'] * item['count']
        cart_text += 'Итого: ' + str(total_price) + '₽'
        bot.send_message(message.chat.id, cart_text, reply_markup=menu.cart_menu())
    elif message.text == 'Оформить заказ':
        User[message.chat.id].state = message.text
        bot.send_message(message.chat.id,
                        'Отлично, рассказывай где находишься!\nЖми кнопку внизу и подожди немного, мы ищем тебя!',
                        reply_markup=menu.send_location_menu())
    elif (message.text == 'Всё правильно, я тут' and User[message.chat.id].state == 'got address'):
        User[message.chat.id].state = 'address valid'
        bot.send_message(message.chat.id, 'Отлично, тогда напиши дополнительную информацию (подъезд, этаж, квартира)',
                        reply_markup=telebot.types.ReplyKeyboardRemove())
    elif (message.text == 'Не, не нашли вы меня' and User[message.chat.id].state == 'got address'):
        User[message.chat.id].state = 'address invalid'
        bot.send_message(message.chat.id, 'Эхх, значит наши спутники барахлят, напиши тогда свой полный адрес сам, пожалуйста',
                        reply_markup=telebot.types.ReplyKeyboardRemove())
    elif User[message.chat.id].state == 'address valid':
        User[message.chat.id].address_info += ' ' + message.text
        User[message.chat.id].state = 'address done'
        api.post_address(message.chat.id, message.from_user.username)
        order_confirmation(message)
    elif User[message.chat.id].state == 'address invalid':
        User[message.chat.id].state = 'address done'
        User[message.chat.id].address_info = message.text
        api.post_address(message.chat.id, message.from_user.username)
        order_confirmation(message)
    elif message.text == 'Да, оформляем!' and User[message.chat.id].state == 'address done':
        order_number = api.proceed_checkout(message.from_user.username)
        bot.send_message(message.chat.id, 'Всё готово! Номер заказа: ' + str(order_number))


def order_confirmation(message):
    number = 0
    total_price = 0
    cart_text = 'Вы заказываете:\n'
    for item in api.get_cart(message.from_user.username):
        number += 1
        cart_text += texts.cartItem.format(str(number), item['menu_position'], item['price'], item['count'])
        total_price += item['price'] * item['count']
    cart_text += 'Итого: ' + str(total_price) + '₽\n\n'
    cart_text += 'Адрес доставки: ' +  User[message.chat.id].address_info + '\n\nВсё верно?'
    bot.send_message(message.chat.id, cart_text, reply_markup=menu.order_confirm_menu())


@bot.message_handler(content_types=['location'])
@db_session
def getting_address(message):
    if User[message.chat.id].state == 'Оформить заказ':
        User[message.chat.id].state = 'got address'
        address = api.get_address(message.location.longitude, message.location.latitude)
        User[message.chat.id].longitude = message.location.longitude
        User[message.chat.id].latitude = message.location.latitude
        User[message.chat.id].address_info = address
        bot.send_message(message.chat.id, 'Твой адрес '+ address + '?',
                        reply_markup=menu.address_confirm_menu())


@bot.callback_query_handler(func=lambda call: True)
@db_session
def callback_query(call):
    if call.data == 'menu':
        User[call.message.chat.id].state = call.message.caption
        bot.send_message(call.message.chat.id, 'Выбирай вкусняхи!', reply_markup=menu.goto_cart_menu())
        for m in api.get_menu_by_delivery(call.message.caption):
            if m['photo_id']:
                bot.send_photo(call.message.chat.id, m['photo_id'],
                               caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                               reply_markup=menu.buy_menu())
            else:
                res = bot.send_photo(call.message.chat.id, urlopen(config.baseImgURL + m['photo']).read(),
                                     caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                                     reply_markup=menu.buy_menu())
                api.upload_menu_photo_id(m['name'], res.photo[0].file_id)
        bot.answer_callback_query(callback_query_id=call.id)
    else:
        menu_name = call.message.caption.split('\n')[0]
        cur_count = api.add_to_cart(call.message.chat.username, User[call.message.chat.id].state, menu_name)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text='Товар добавлен, в корзине: ' + str(cur_count))


bot.polling(none_stop=True)
