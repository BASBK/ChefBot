import requests
import config
import json
from models import *


def get_categories():
    result = []
    r = requests.get(config.baseURL + 'delivery_types')
    if r.status_code == requests.codes.ok:
        if r.json() is not None:
            for row in r.json():
                result.append(row['type_name'])
    return result


def get_deliveries(type):
    result = []
    r = requests.get(config.baseURL + 'deliveries/' + type)
    if r.status_code == requests.codes.ok:
        if r.json() is not None:
            for row in r.json():
                result.append(row)
    return result


def get_menu_by_delivery(delivery):
    r = requests.get(config.baseURL + 'menu/' + delivery)
    if r.status_code == requests.codes.ok and r.json() is not None:
        return r.json()
    return None


def get_menu():
    r = requests.get(config.baseURL + 'menu')
    if r.status_code == requests.codes.ok and r.json() is not None:
        return r.json()
    return None


def upload_menu_photo_id(menu_name, photo_id):
    param = {'photo_id': photo_id}
    r = requests.put(config.baseURL + 'menu/' + menu_name + '/photo', params=param)
    if r.status_code == requests.codes.ok:
        return r
    return None


def upload_delivery_photo_id(d_name, photo_id):
    param = {'photo_id': photo_id}
    r = requests.put(config.baseURL + 'deliveries/' + d_name + '/photo', params=param)
    if r.status_code == requests.codes.ok:
        return r
    return None


def add_to_cart(client, delivery, menu_name):
    data = {}
    data['delivery'] = delivery
    data['menu_name'] = menu_name
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.post(config.baseURL + 'cart/' + client, json=jdata)
    if r.status_code == requests.codes.ok:
        if r.json() is not None:
            return r.json()['count']
    return 0


def clear_cart(client):
    data = {'whole': True}
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.delete(config.baseURL + 'cart/' + client, json=jdata)
    if r.status_code == requests.codes.ok:
        return r
    return None


def get_cart(client):
    r = requests.get(config.baseURL + 'cart/' + client)
    if r.status_code == requests.codes.ok:
        if r.json() is not None:
            return r.json()
    return None


def get_address(long, lat):
    url = 'https://geocode-maps.yandex.ru/1.x/?geocode={0},{1}&format=json&results=1'
    r = requests.get(url.format(long, lat))
    if r.json() is not None:
        return r.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    return None


def post_address(chatID, client):
    data = {}
    data['username'] = client
    data['longitude'] = User[chatID].longitude
    data['latitude'] = User[chatID].latitude
    data['additional_info'] = User[chatID].address_info
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.post(config.baseURL + 'clients', json=jdata)
    if r.status_code == requests.codes.ok:
        return r
    return None


def proceed_checkout(client):
    r = requests.post(config.baseURL + 'orders/' + client)
    if r.status_code == requests.codes.ok:
        if r.json() is not None:
            return r.json()
    return None


def check_if_staff(username, chatID):
    data = {'chatID': chatID}
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.put(config.baseURL + 'staff/' + username, json=jdata)
    if r.status_code == requests.codes.ok:
        return r
    return None


def update_order(number):
    r = requests.put(config.baseURL + 'orders/' + number)
    return r.json()


def finish_order(courier):
    r = requests.put(config.baseURL + 'orders/courier/' + courier)
    if r.status_code == requests.codes.ok:
        return r
    return None
