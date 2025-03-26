from flask_login import UserMixin
from extensions import mysql


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def get_id(self):
        return str(self.id)


def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return User(user[0], user[1], user[2]) if user else None
