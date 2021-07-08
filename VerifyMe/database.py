import sqlite3
import os


class Database:
    DB_KEYS = ("macid", "is_verified", "stream", "specialty",
               "discord_name", "discord_id", "is_TA", "is_upper_year")
    DB_TYPES = ("text", "integer", "text", "text",
                "text", "text", "integer", "integer")
    DB_PROTOTYPE = str(tuple(f"{key} {type}" for key, type in zip(
        DB_KEYS, DB_TYPES))).replace('\'', '')

    @staticmethod
    def new_user(macid):
        return macid, 0, None, None, None, None, 0, 0

    class User(dict):
        def __init__(self, database, values):
            self.database = database
            super().__init__(zip(Database.DB_KEYS, values))

        def __setitem__(self, key, value):
            conn = sqlite3.connect(self.database.path)
            cur = conn.cursor()

            cur.execute(
                f"UPDATE users SET {key} = ? WHERE macid = ?", (value, self["macid"]))

            conn.commit()
            cur.close()
            conn.close()

            self.database.cache[self["macid"]] = self
            return super().__setitem__(key, value)

    def create_db(self, macids):
        if os.path.isfile(self.path):
            return False

        conn = sqlite3.connect(self.path)
        cur = conn.cursor()

        cur.execute(f"CREATE TABLE users {Database.DB_PROTOTYPE}")
        cur.executemany(f"INSERT INTO users VALUES (?{', ?' * (len(Database.DB_KEYS) - 1)})",
                        (Database.new_user(macid) for macid in macids))

        conn.commit()
        cur.close()
        conn.close()

    def __init__(self, path):
        self.path = path
        self.cache = {}

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]

        conn = sqlite3.connect(self.path)
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE macid = ?", (key,))
        val = cur.fetchone()

        cur.close()
        conn.close()

        if val:
            val = Database.User(self, val)
            self.cache[key] = val
        return val

    def __contains__(self, item):
        return self.__getitem__(item) != None
