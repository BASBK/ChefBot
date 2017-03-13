import requests
import config


def get_categories():
    result = []
    r = requests.get(config.baseURL + 'delivery_types')
    for row in r.json():
        result.append(row['type_name'])
    return result


def get_deliveries(type):
    result = []
    r = requests.get(config.baseURL + 'deliveries', params={'dtype': type})
    for row in r.json():
        result.append(row['name'])
    return result


def get_menu_by_delivery(delivery):
    r = requests.get(config.baseURL + 'menu/' + delivery)
    return r.json()


def get_menu():
    r = requests.get(config.baseURL + 'menu')
    return r.json()


def upload_photo_id(menu_name, photo_id):
    param = {'photo_id' : photo_id}
    r = requests.put(config.baseURL + 'menu/' + menu_name, params=param)
    return r
