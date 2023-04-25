import os
from sqlite3 import connect


class Club:
    name: str = None
    uri: str = None
    id: int = None
    __exists: bool = None

    def __init__(self, club_id):
        if club_id is None:
            return
        with connect(os.environ.get("DB_PATH")) as con:
            cur = con.cursor()
            sql = "select * from clubs WHERE club_id=?"
            cur.execute(sql, club_id)
            rows = cur.fetchall()
            if len(rows) == 0:
                self.__exists = False
                return
            self.__exists = True
            self.name = rows[0][1]
            self.uri = rows[0][2]
            self.id = club_id

    def exists(self):
        return self.__exists

    def join(self, user_id, admin=False):
        if user_id is None:
            return 'No such User'
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                # check if already joined
                sql = "select * from usersInClubs WHERE club_id=? and user_id=? and endTime is null"
                cur.execute(sql, [self.id, user_id])
                rows = cur.fetchall()
                if len(rows) > 0:
                    return "User already joined"

                # join if necessary
                sql2 = "INSERT INTO usersInClubs (user_id, club_id, admin) VALUES (?,?,?)"
                cur.execute(sql2, [user_id, self.id, 1 if admin else 0])

                sql3 = "SELECT event_db_id FROM events WHERE club_id=?"
                events = cur.execute(sql3, self.id).fetchall()

                for e in events:
                    sql4 = "INSERT INTO attendance (event_id, user_id) VALUES (?,?)"
                    cur.execute(sql4, [e[0], user_id])

        except Exception as e:
            print(e)
            con.rollback()
            return "Database Error"

    def leave(self, user_id):
        if user_id is None:
            return 'No such User'
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                sql = "UPDATE usersInClubs SET endTime=current_timestamp"
                cur.execute(sql)
        except Exception as e:
            print(e)
            con.rollback()
            return "Database Error"

    def getMembers(self):
        try:
            with connect(os.environ.get("DB_PATH")) as con:
                cur = con.cursor()
                sql = "SELECT * FROM usersInClubs INNER JOIN users u on u.user_id = usersInClubs.user_id WHERE club_id=? and endTime is null"
                cur.execute(sql, self.id)
                members = cur.fetchall()

                return map(lambda x: x[5], members),map(lambda x: x[1], members)
        except Exception as e:
            print(e)
            con.rollback()
            return "Database Error"

    def getIncomingTrainingsStats(self, n):
        # try:
        #     with connect(os.environ.get("DB_PATH")) as con:
        #         cur = con.cursor()
        #         sql = "SELECT * FROM usersInClubs INNER JOIN users u on u.user_id = usersInClubs.user_id WHERE club_id=? and endTime is null"
        #         cur.execute(sql, self.id)
        #         members = cur.fetchall()
        #         print(members)
        #         return map(lambda x: x[5], members)
        # except Exception as e:
        #     print(e)
        #     con.rollback()
        #     return "Database Error"
        pass



    def event_ids(self):
        with connect(os.environ.get("DB_PATH")) as con:
            cur = con.cursor()
            sql = f"SELECT event FROM events WHERE club_id=?"
            r = cur.execute(sql, self.id).fetchall()

            return map(lambda x: x[0], r)