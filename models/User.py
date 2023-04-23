import os
from sqlite3 import connect


class User:
    def __init__(self, credentials,info):
        self.credentials = credentials
        self.info = info
    def save(self):
        if self.exists():
            return
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                last_id = cur.execute(f'select max(user_id) from users').fetchall()[0][0]
                if last_id is None:
                    last_id = 0

                sql = f"INSERT INTO users (user_id, mail) VALUES (?,?)"
                cur.execute(sql, [self.info['id'], self.info['email']])
                con.commit()
        except Exception as e:
            print(e)
            con.rollback()

    def exists(self):
        with connect(os.environ.get("DB_PATH")) as con:
            cur = con.cursor()
            # check if already exists
            sql = "select * from users WHERE user_id=?"
            cur.execute(sql, (self.info['id'],))
            rows = cur.fetchall()
            return len(rows) > 0


