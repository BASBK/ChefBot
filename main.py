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

# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
@db_session
def handle_start(message):
    if message.from_user.username is None:
        bot.send_message(message.chat.id, 'Воу, похоже, что ты не указал никнейм когда регистрировался в Телеграмме. ' +
                        'Укажи его, пожалуйста в настройках программы, чтобы я мог с тобой работать')
    else:
        api.check_if_staff(message.from_user.username, message.chat.id)
        if not User.exists(chatID=message.chat.id):
            User(chatID=message.chat.id, username=message.from_user.username, state=config.STATE_START)
        User[message.chat.id].state = config.STATE_START
        bot.send_message(message.chat.id, '👨‍🍳 Приветствую! Что желаете откушать?', reply_markup=menu.category_menu())


@bot.message_handler(func=lambda message: message.chat.username != None, content_types=['text'])
@db_session
def handle_text(message):
    if not User.exists(chatID=message.chat.id):
        User(chatID=message.chat.id, username=message.from_user.username, state=config.STATE_START)
        bot.send_message(message.chat.id, '👨‍🍳 Приветствую! Что желаете откушать?', reply_markup=menu.category_menu())
    elif User[message.chat.id].state == config.STATE_START and message.text in api.get_categories():
        User[message.chat.id].state = message.text
        bot.send_message(message.chat.id, '🚚 А вот и все доставочки, выбирай!', reply_markup=menu.goto_home_menu())
        send_deliveries(message)
    elif message.text == '🛍 На главную':
        User[message.chat.id].state = config.STATE_START
        bot.send_message(message.chat.id, '👨‍🍳 Приветствую! Что желаете откушать?', reply_markup=menu.category_menu())
    elif message.text == '🛒 Корзина':
        User[message.chat.id].state = config.STATE_IN_CART
        send_cart(message)
    elif message.text == '🍽 Добавить ещё еды!' and User[message.chat.id].state == config.STATE_IN_CART:
        User[message.chat.id].state = config.STATE_START
        bot.send_message(message.chat.id, 'Выбирай вкусняхи!', reply_markup=menu.goto_cart_menu())
        send_menu(User[message.chat.id].in_menu, message.chat.id)
    elif message.text == '🗑 Очистить корзину' and User[message.chat.id].state == config.STATE_IN_CART:
        User[message.chat.id].state = config.STATE_START
        api.clear_cart(message.from_user.username)
        bot.send_message(message.chat.id, 'Приветствую! Что желаете откушать?', reply_markup=menu.category_menu())
    elif message.text == '✅ Оформить заказ' and User[message.chat.id].state == config.STATE_IN_CART:
        User[message.chat.id].state = config.STATE_CHECKOUT
        bot.send_message(message.chat.id,
                        'Отлично, рассказывай где находишься!\nЖми кнопку внизу и подожди немного, мы ищем тебя!',
                        reply_markup=menu.send_location_menu())
    elif message.text == '👍 Всё правильно, я тут' and User[message.chat.id].state == config.STATE_OBTAIN_GPS_ADDRESS:
        User[message.chat.id].state = config.STATE_VALID_ADDRESS
        bot.send_message(message.chat.id, '✏️ Отлично, тогда напиши дополнительную информацию (подъезд, этаж, квартира)',
                        reply_markup=telebot.types.ReplyKeyboardRemove())
    elif message.text == '👎 Не, не нашли вы меня' and User[message.chat.id].state == config.STATE_OBTAIN_GPS_ADDRESS:
        User[message.chat.id].state = config.STATE_INVALID_ADDRESS
        bot.send_message(message.chat.id, '📡💥 Эхх, значит наши спутники барахлят, напиши тогда свой полный адрес сам, пожалуйста',
                        reply_markup=telebot.types.ReplyKeyboardRemove())
    elif User[message.chat.id].state == config.STATE_VALID_ADDRESS:
        User[message.chat.id].address_info += ', ' + message.text
        User[message.chat.id].state = config.STATE_OBTAIN_FULL_ADDRESS
        api.post_address(message.chat.id, message.from_user.username)
        order_confirmation(message)
    elif User[message.chat.id].state == config.STATE_INVALID_ADDRESS:
        User[message.chat.id].address_info = message.text
        User[message.chat.id].state = config.STATE_OBTAIN_FULL_ADDRESS
        api.post_address(message.chat.id, message.from_user.username)
        order_confirmation(message)
    elif message.text == '✅ Да, оформляем!' and User[message.chat.id].state == config.STATE_OBTAIN_FULL_ADDRESS:
        order = api.proceed_checkout(message.from_user.username)
        bot.send_message(message.chat.id, 'Всё готово! Номер заказа: ' + str(order['order_number']), reply_markup=menu.goto_home_menu())
        send_to_cook(order)
    elif message.text == '❌ Отмена' and User[message.chat.id].state == config.STATE_OBTAIN_FULL_ADDRESS:
        User[message.chat.id].state = config.STATE_START
        bot.send_message(message.chat.id, '👨‍🍳 Приветствую! Что желаете откушать?', reply_markup=menu.category_menu())


def send_deliveries(message):
    for d in api.get_deliveries(message.text):
        if d['photo_id']:
            bot.send_photo(message.chat.id, d['photo_id'], caption=d['name'], reply_markup=menu.delivery_menu())
        else:
            res = bot.send_photo(message.chat.id, urlopen(config.baseImgURL + d['photo']).read(),
                                 caption=d['name'], reply_markup=menu.delivery_menu())
            api.upload_delivery_photo_id(d['name'], res.photo[0].file_id)


def send_cart(message):
    number = 0
    total_price = 0
    cart = api.get_cart(message.from_user.username)
    if cart is None:
        bot.send_message(message.chat.id, 'Пустовато тут пока :(', reply_markup=menu.goto_home_menu())
    else:
        cart_text = 'В Вашей корзине:\n'
        for item in cart:
            number += 1
            cart_text += texts.cartItem.format(str(number), item['menu_position'], item['price'], item['count'])
            total_price += item['price'] * item['count']
        cart_text += 'Итого: ' + str(total_price) + '₽'
        bot.send_message(message.chat.id, cart_text, reply_markup=menu.cart_menu())


def order_confirmation(message):
    number = 0
    total_price = 0
    cart_text = 'Вы заказываете:\n'
    cart = api.get_cart(message.from_user.username)
    if cart is not None:
        for item in cart:
            number += 1
            cart_text += texts.cartItem.format(str(number), item['menu_position'], item['price'], item['count'])
            total_price += item['price'] * item['count']
        cart_text += 'Итого: ' + str(total_price) + '₽\n\n'
        cart_text += 'Адрес доставки: ' +  User[message.chat.id].address_info + '\n\nВсё верно?'
        bot.send_message(message.chat.id, cart_text, reply_markup=menu.order_confirm_menu())


def send_to_cook(order):
    number = 0
    new_order = 'Заказ №' + str(order['order_number']) + '\n'
    for item in order['menu']:
        number += 1
        new_order += texts.newOrderItem.format(str(number), item['name'], item['count'])
    bot.send_message(order['cook'], new_order, reply_markup=menu.cook_menu())

@bot.message_handler(content_types=['text'])
def ask_for_username(message):
    bot.send_message(message.chat.id, 'Воу, похоже, что ты не указал никнейм когда регистрировался в Телеграмме. ' +
                    'Укажи его, пожалуйста в настройках программы, чтобы я мог с тобой работать')

@bot.message_handler(content_types=['location'])
@db_session
def getting_address(message):
    if User[message.chat.id].state == config.STATE_CHECKOUT:
        address = api.get_address(message.location.longitude, message.location.latitude)
        User[message.chat.id].state = config.STATE_OBTAIN_GPS_ADDRESS
        User[message.chat.id].longitude = message.location.longitude
        User[message.chat.id].latitude = message.location.latitude
        User[message.chat.id].address_info = address
        bot.send_message(message.chat.id, 'Твой адрес '+ address + '?', reply_markup=menu.address_confirm_menu())


@bot.callback_query_handler(func=lambda call: True)
@db_session
def callback_query(call):
    if call.data == 'menu':
        User[call.message.chat.id].in_menu = call.message.caption
        bot.send_message(call.message.chat.id, 'Выбирай вкусняхи!', reply_markup=menu.goto_cart_menu())
        send_menu(call.message.caption, call.message.chat.id)
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == 'add_to_cart':
        menu_name = call.message.caption.split('\n')[0]
        cur_count = api.add_to_cart(call.message.chat.username, User[call.message.chat.id].in_menu, menu_name)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text='Товар добавлен, в корзине: ' + str(cur_count))
    elif call.data == 'cook_receive':
        number = call.message.text.split('\n')[0].split('№')[1]
        further_info = api.update_order(number)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=menu.cook_done_menu())
        print(further_info['client'])
        client_id = User.get(username=further_info['client']).chatID
        send_to_courier(further_info)
        bot.send_message(client_id, 'Ваш заказ приготовлен, информация передана курьеру!')
    elif call.data == 'courier_receive':
        api.finish_order(call.message.chat.username)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=menu.courier_done_menu())


def send_to_courier(info):
    number = 0
    order = 'Заказ №' + str(info['order_number']) + '\n'
    order += 'Клиент: @' + info['client'] + '\n'
    for item in info['menu']:
        number += 1
        order += texts.newOrderItem.format(str(number), item['name'], item['count'])
    order += 'Адрес: ' + info['address']['text']
    bot.send_message(info['courier'], order)
    bot.send_location(info['courier'], latitude=info['address']['lat'], longitude=info['address']['long'],
                      reply_markup=menu.courier_menu())


def send_menu(delivery_name, chat_id):
    menus = api.get_menu_by_delivery(delivery_name)
    if menus is not None:
        for m in menus:
            if m['photo_id']:
                bot.send_photo(chat_id, m['photo_id'],
                               caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                               reply_markup=menu.buy_menu())
            else:
                res = bot.send_photo(chat_id, urlopen(config.baseImgURL + m['photo']).read(),
                                     caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                                     reply_markup=menu.buy_menu())
                api.upload_menu_photo_id(m['name'], res.photo[0].file_id)


bot.polling(none_stop=True)
