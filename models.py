from pony.orm import *

db = Database()


class User(db.Entity):
    chatID = PrimaryKey(int)
    username = Required(str)
    state = Required(str)
    in_menu = Optional(str)
    longitude = Optional(float)
    latitude = Optional(float)
    address_info = Optional(str)


db.bind('sqlite', 'users.db', create_db=True)
db.generate_mapping(create_tables=True)
