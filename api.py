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


def get_menu(delivery):
    r = requests.get(config.baseURL + 'menu/' + delivery)
    return r.json()