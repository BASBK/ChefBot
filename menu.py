from telebot import types
import api


def category_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    for row in api.get_categories():
        user_markup.add(row)
    return user_markup


def delivery_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('Меню', callback_data='menu'))
    return user_inline


def buy_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('Купить', callback_data='buy'))
    return user_inline
