import os
from sqlite3 import connect


class Club:
    name: str = None
    uri: str = None
    id: int = None
    __exists: bool = None

    def __init__(self, clubID):
        with connect(os.environ.get("DB_PATH")) as con:
            cur = con.cursor()
            sql = "select * from clubs WHERE club_id=?"
            cur.execute(sql, clubID)
            rows = cur.fetchall()
            if len(rows) == 0:
                self.__exists = False
                return
            self.__exists = True
            self.name = rows[0][1]
            self.uri = rows[0][2]

    def exists(self):
        return self.__exists
