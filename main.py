import telebot
import config
import menu
import api
import texts
import requests
import json
from flask import Flask

app = Flask(__name__)

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.from_user.id, 'Хаюхай!', reply_markup=menu.category_menu())


def get_FileID(id):
    #r = bot.download_file('c:\ChefBot\pizza.jpg')
    r = requests.get('https://api.telegram.org/bot' + config.token + '/SendPhoto?chat_id=' + str(id) + '&photo=https://www.littlecaesarsaz.com/wp-content/uploads/2017/03/pizza-3.jpg')
    print(r.json())


@bot.message_handler(content_types=['text'])
def handle_start(message):
    if message.text == 'Пиццерия':
        # get_FileID(message.chat.id)
        for d in api.get_deliveries(message.text):
            photo = open('tashir.jpg', 'rb')
            bot.send_photo(message.from_user.id, photo, caption=d, reply_markup=menu.delivery_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'menu':
        bot.answer_callback_query(callback_query_id=call.id)
        for m in api.get_menu_by_delivery(call.message.caption):
            if m['photo_id'] != '':
                print('from bd')
                bot.send_photo(call.message.chat.id, m['photo_id'],
                               caption=texts.menuItem.format(m['name'], m['description'],m['weight'], m['price']),
                               reply_markup=menu.buy_menu())
            else:
                print('from pc')
                res = bot.send_photo(call.message.chat.id, open('pizza.jpg', 'rb'),
                                     caption=texts.menuItem.format(m['name'], m['description'], m['weight'], m['price']),
                                     reply_markup=menu.buy_menu())
                api.upload_photo_id(m['name'], res.photo[0].file_id)


bot.polling(none_stop=True)
