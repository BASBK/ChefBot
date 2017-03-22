import requests
import config
import json

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


def add_to_basket(client, delivery, menu_name, count):
    data = {}
    data['delivery'] = delivery
    data['menu_name'] = menu_name
    data['count'] = count
    jdata = json.dumps(data, ensure_ascii=False)
    r = requests.post(config.baseURL + 'basket/' + str(client), json=jdata)
    return r
