import requests
import config
import json
from models import *


def get_categories():
    result = []
    r = requests.get(config.baseURL + 'delivery_types')
    for row in r.json():
        result.append(row['type_name'])
    return result


def get_deliveries(type):
    result = []
    r = requests.get(config.baseURL + 'deliveries/' + type)
    for row in r.json():
        result.append(row)
    return result


def get_menu_by_delivery(delivery):
    r = requests.get(config.baseURL + 'menu/' + delivery)
    return r.json()


def get_menu():
    r = requests.get(config.baseURL + 'menu')
    return r.json()


def upload_menu_photo_id(menu_name, photo_id):
    param = {'photo_id': photo_id}
    r = requests.put(config.baseURL + 'menu/' + menu_name + '/photo', params=param)
    return r


def upload_delivery_photo_id(d_name, photo_id):
    param = {'photo_id': photo_id}
    r = requests.put(config.baseURL + 'deliveries/' + d_name + '/photo', params=param)
    return r


def add_to_cart(client, delivery, menu_name):
    data = {}
    data['delivery'] = delivery
    data['menu_name'] = menu_name
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.post(config.baseURL + 'cart/' + client, json=jdata)
    return r.json()['count']


def get_cart(client):
    r = requests.get(config.baseURL + 'cart/' + client)
    return r.json()


def get_address(long, lat):
    url = 'https://geocode-maps.yandex.ru/1.x/?geocode={0},{1}&format=json&results=1'
    r = requests.get(url.format(long, lat))
    return r.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']


def post_address(chatID, client):
    data = {}
    data['username'] = client
    data['longitude'] = User[chatID].longitude
    data['latitude'] = User[chatID].latitude
    data['additional_info'] = User[chatID].address_info
    jdata = json.dumps(data, ensure_ascii=False)
    print(jdata)
    r = requests.post(config.baseURL + 'clients', json=jdata)
    return r


def proceed_checkout(client):
    r = requests.post(config.baseURL + 'orders/' + client)
    return r.json()['order_number']
