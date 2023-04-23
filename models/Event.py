import os
from sqlite3 import connect


class Event:

    # @staticmethod
    def add(self, e, at_ids):
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                last_id = cur.execute(f'select max(event_db_id) from events').fetchall()[0][0]
                if last_id is None:
                    last_id = 0

                sql = f"INSERT INTO events (event_db_id, summary, description, startDateTime, startTimeZone, endDateTime, endTimeZone, event)" \
                      f"VALUES (?,?,?,?,?,?,?,?)"
                cur.execute(sql, (
                last_id + 1, e['summary'], 'desc', e['start']['dateTime'], 'CET', e['end']['dateTime'], 'CET', e['id']))
                event_id = cur.lastrowid
                # adding to attendance
                for id in at_ids:
                    print(id)
                    sql2 = "INSERT INTO attendance (event_id, user_id) VALUES (?,?)"
                    cur.execute(sql2, (event_id, id))

                con.commit()
        except Exception as e:
            print(e)
            con.rollback()

    def remove(self, event_id):
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                sql = f" DELETE FROM events WHERE event=? "
                cur.execute(sql, [event_id])
                con.commit()
        except Exception as e:
            print(e)
            con.rollback()

    def edit(self, event_id, updated_event):
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                sql = f" UPDATE events SET summary = ?, startDateTime = ?, endDateTime = ? WHERE event= ?"
                cur.execute(sql, (
                updated_event['summary'], updated_event['start']['dateTime'], updated_event['end']['dateTime'],
                event_id))
                con.commit()
        except Exception as e:
            print(e)
            con.rollback()
