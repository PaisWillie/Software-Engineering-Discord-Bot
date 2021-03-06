import sqlite3
import os
import csv
from typing import NamedTuple, Optional


class Database:
    class UserData(NamedTuple):
        macid: str
        full_name: str
        is_verified: int
        stream: str
        specialty: Optional[str]
        discord_name: Optional[str]
        discord_id: Optional[str]
        is_TA: int

        @classmethod
        def new(cls, macid: str, full_name: str, stream: str, specialty: str, is_TA: int):
            return cls(macid, full_name, 0, stream, specialty, None, None, is_TA)

    DB_KEYS = UserData._fields
    DB_TYPES = ("text", "text", "integer", "text",
                "text", "text", "text", "integer")
    DB_PROTOTYPE = str(tuple(f"{key} {type}" for key, type in zip(
        DB_KEYS, DB_TYPES))).replace('\'', '')

    class User(dict):
        def __init__(self, database, values):
            self.database = database
            super().__init__(zip(Database.DB_KEYS, values))

        def __setitem__(self, key, value):
            entry_key = Database.DB_KEYS[0]
            entry_val = self[entry_key]

            conn = sqlite3.connect(self.database.path)
            cur = conn.cursor()

            cur.execute(
                f"UPDATE users SET {key} = ? WHERE {entry_key} = ?", (value, entry_val))

            conn.commit()
            cur.close()
            conn.close()

            super().__setitem__(key, value)
            # if reassigning macid for some reason, invalidate cached value
            if key == entry_key:
                del self.database.cache[entry_val]
            self.database.cache[self[entry_key]] = self

    @staticmethod
    def from_classlist(path, stream : str) -> list[UserData]:
        users = []
        with open(path, "r", newline='') as csv_in:
            reader = csv.reader(csv_in, delimiter=',', quotechar="\"")
            for _image, full_name, macid, role in reader:
                is_TA = int(role != "Student")
                users.append(Database.UserData.new(macid, full_name, stream, None, is_TA))
        return users

    @staticmethod
    def create_db(path, users : list[tuple]):
        if os.path.isfile(path):
            raise FileExistsError(f"File \"{path}\" already exists")

        conn = sqlite3.connect(path)
        cur = conn.cursor()

        cur.execute(f"CREATE TABLE users {Database.DB_PROTOTYPE}")
        cur.executemany(f"INSERT INTO users VALUES (?{', ?' * (len(Database.DB_KEYS) - 1)})", users)
        conn.commit()

        cur.close()
        conn.close()

    def __init__(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File \"{path}\" does not exist")
        self.path = path
        self.cache : dict[str, Database.User] = {}

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        entry_key = Database.DB_KEYS[0]

        conn = sqlite3.connect(self.path)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM users WHERE {entry_key} = ?", (key,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            user = Database.User(self, user)
            self.cache[key] = user
        return user

    def __contains__(self, item):
        return self.__getitem__(item) != None


def main():
    cwd = os.path.dirname(__file__)
    classlists = os.path.join(cwd, "classlists")

    users = {user.macid: user for user in set(
        Database.from_classlist(path=os.path.join(classlists, "2DA4.csv"), stream="Software") +
        Database.from_classlist(path=os.path.join(classlists, "2GA3.csv"), stream="Software") +
        Database.from_classlist(path=os.path.join(classlists, "2DM3.csv"), stream="Software") +
        Database.from_classlist(path=os.path.join(classlists, "2OP3.csv"), stream="Software") +
        Database.from_classlist(path=os.path.join(classlists, "2XC3.csv"), stream="Software")
    )}
    for mgmt_user in Database.from_classlist(path=os.path.join(classlists, "ENGNMGT_2AA3.csv"), stream="_"):
        try:
            user = users[mgmt_user.macid]
            users[mgmt_user.macid] = Database.UserData.new(
                user.macid, user.full_name, user.stream, "Management", user.is_TA)
        except: pass
    for soc_user in Database.from_classlist(path=os.path.join(classlists, "ENGSOCTY_2Y03.csv"), stream="_"):
        try:
            user = users[soc_user.macid]
            users[soc_user.macid] = Database.UserData.new(
                user.macid, user.full_name, user.stream, "Society", user.is_TA)
        except: pass
    for bio_user in Database.from_classlist(path=os.path.join(classlists, "IBEHS_2P03.csv"), stream="_"):
        try:
            user = users[bio_user.macid]
            users[bio_user.macid] = Database.UserData.new(
                user.macid, user.full_name, user.stream, "Biomedical", user.is_TA)
        except: pass

    Database.create_db(path=os.path.join(cwd, "users.db"), users=list(users.values()))

if __name__ == '__main__':
    main()