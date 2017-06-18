from telebot import types
import api
import config


def category_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    for row in api.get_categories():
        user_markup.add(row)
    return user_markup


def delivery_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('📃 Меню', callback_data='menu'))
    return user_inline


def buy_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('🍽 Добавить в корзину', callback_data='add_to_cart'))
    return user_inline


def cook_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('☑️ Готово', callback_data='cook_receive'))
    return user_inline


def cook_done_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('✅ Готово', callback_data='cook_done'))
    return user_inline


def courier_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('☑️ Готово', callback_data='courier_receive'))
    return user_inline


def courier_done_menu():
    user_inline = types.InlineKeyboardMarkup()
    user_inline.add(types.InlineKeyboardButton('✅ Готово', callback_data='courier_done'))
    return user_inline


def goto_cart_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.add('🛒 Корзина')
    return user_markup


def cart_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.add('✅ Оформить заказ', '🍽 Добавить ещё еды!')
    user_markup.add('🗑 Очистить корзину')
    user_markup.add('🛍 На главную')
    return user_markup


def goto_home_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.add('🛍 На главную')
    return user_markup


def send_location_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    location_btn = types.KeyboardButton(text='📡 Отправить своё местоположение', request_location=True)
    user_markup.add(location_btn)
    return user_markup


def address_confirm_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.add('👍 Всё правильно, я тут')
    user_markup.add('👎 Не, не нашли вы меня')
    return user_markup


def order_confirm_menu():
    user_markup = types.ReplyKeyboardMarkup(True, False)
    user_markup.add('✅ Да, оформляем!', '❌ Отмена')
    return user_markup
