from pony.orm import *

db = Database()


class User(db.Entity):
    chatID = PrimaryKey(int)
    state = Required(str)


db.bind('sqlite', 'users.db', create_db=True)
db.generate_mapping(create_tables=True)
