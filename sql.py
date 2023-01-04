import sqlite3

from datetime import datetime


# check if user not in db add user in db 'shop' to 'users'
def check_and_add_user(message):
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    cur.execute("SELECT user_id FROM users")
    db_users = cur.fetchall()
    if message not in db_users:
        cur.execute('INSERT or IGNORE INTO users\n'
                    '(user_id, username, first_name, last_name, date)\n'
                    'VALUES (?, ?, ?, ?, ?)', (message.from_user.id,
                                               message.from_user.username,
                                               message.from_user.first_name,
                                               message.from_user.last_name,
                                               datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()
    cur.close()
    return


# add item in db
def add_shoes_db(model, price, description, gender, foto1, foto2, foto3):
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    cur.execute('INSERT INTO shoes\n'
                '(model, description, gender, price, foto1, foto2, foto3)\n'
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (model, description, gender, price, foto1, foto2, foto3))
    con.commit()
    cur.close()


def clean_db_orders():
    con = sqlite3.connect('shop.db')
    cur = con.cursor()
    cur.execute(f'DELETE FROM orders')
    con.commit()
    cur.close()
