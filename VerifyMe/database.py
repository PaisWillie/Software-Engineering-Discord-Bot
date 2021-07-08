import sqlite3
import os
import csv
from collections import namedtuple


class Database:
    DB_KEYS = ("macid", "full_name", "is_verified", "stream",
               "specialty", "discord_name", "discord_id", "is_TA")
    DB_TYPES = ("text", "text", "integer", "text",
                "text", "text", "text", "integer")
    DB_PROTOTYPE = str(tuple(f"{key} {type}" for key, type in zip(
        DB_KEYS, DB_TYPES))).replace('\'', '')


    UserData = namedtuple("UserData", " ".join(DB_KEYS))

    @staticmethod
    def new_user(macid, full_name, stream, is_TA) -> UserData:
        return Database.UserData(macid, full_name, 0, stream, None, None, None, is_TA)

    @staticmethod
    def from_classlist(filepath, stream) -> list[UserData]:
        users = []
        with open(filepath, "r", newline='') as csv_in:
            reader = csv.reader(csv_in, delimiter=',', quotechar="\"")
            for image, full_name, macid, role in reader:
                is_TA = int(role != "Student")
                users.append(Database.new_user(macid, full_name, stream, is_TA))

        return users

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

    def create_db(self, users : list[tuple]):
        if os.path.isfile(self.path):
            return False

        conn = sqlite3.connect(self.path)
        cur = conn.cursor()

        cur.execute(f"CREATE TABLE users {Database.DB_PROTOTYPE}")
        cur.executemany(f"INSERT INTO users VALUES (?{', ?' * (len(Database.DB_KEYS) - 1)})", users)

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


def main():
    db = Database("VerifyMe/users.db")
    user_data = list(set(
        Database.from_classlist("VerifyMe/classlists/2DA4.csv", "Software") +
        Database.from_classlist("VerifyMe/classlists/2GA3.csv", "Software")))
    db.create_db(user_data)

if __name__ == '__main__':
    main()