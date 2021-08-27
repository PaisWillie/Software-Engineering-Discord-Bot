import os
from unittest import TestCase, main
from VerifyMe.database import Database


class TestDatabase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cwd = os.path.dirname(__file__)
        cls.clist_dir = os.path.join(cls.cwd, "../VerifyMe/classlists")
        cls.fn = "test.db"
        cls.target = os.path.join(cls.cwd, cls.fn)
        cls.test_user1 = Database.UserData(
            macid="quattrl",
            full_name="Quattrociocchi, Luigi",
            is_verified=0,
            stream="Software",
            specialty=None,
            discord_name=None,
            discord_id=None,
            is_TA=0)
        # db[mac_id]["is_verified"] = 1
        # db[mac_id]["discord_name"] = str(member)
        # db[mac_id]["discord_id"] = str(member.id)
        cls.test_user2 = Database.UserData(
            macid="quattrl",
            full_name="Quattrociocchi, Luigi",
            is_verified=1,
            stream="Software",
            specialty=None,
            discord_name="luigi",
            discord_id="196045824881328129",
            is_TA=0)


    def tearDown(self):
        try:
            os.remove(self.target)
        except FileNotFoundError:
            pass

    def typical_db(self):
        Database.create_db(
            path=self.target,
            users=list(set(
                Database.from_classlist(
                    path=os.path.join(self.clist_dir, "2DA4.csv"),
                    stream="Software") +
                Database.from_classlist(
                    path=os.path.join(self.clist_dir, "2GA3.csv"),
                    stream="Software")
            )))
        return Database(path=self.target)


    def test_create_db(self):
        Database.create_db(path=self.target, users=[])
        self.assertIn(self.fn, os.listdir(self.cwd))

    def test_create_db_fail(self):
        Database.create_db(path=self.target, users=[])
        with self.assertRaises(FileExistsError):
            Database.create_db(path=self.target, users=[])

    def test_init(self):
        Database.create_db(path=self.target, users=[])
        db = Database(path=self.target)
        self.assertIsInstance(db, Database)
    
    def test_init_typical(self):
        db =  self.typical_db()
        self.assertIsInstance(db, Database)

    def test_init_fail(self):
        with self.assertRaises(FileNotFoundError):
            db = Database(path=self.target)

    def test_from_classlist(self):
        len1 = 142
        len2 = 178
        cl1 = Database.from_classlist(
            path=os.path.join(self.clist_dir, "2DA4.csv"),
            stream="Software")
        cl2 = Database.from_classlist(
            path=os.path.join(self.clist_dir, "2GA3.csv"),
            stream="Software")
        
        self.assertEqual(len(cl1), len1)
        self.assertEqual(len(cl2), len2)
        self.assertLess(len(set(cl1 + cl2)), len1 + len2)
        self.assertIn(self.test_user1, cl1)
        self.assertNotIn(self.test_user2, cl1)

    def test_getitem(self):
        db = self.typical_db()
        got_user = db["quattrl"]
        for field, val in got_user.items():
            self.assertEqual(val, getattr(self.test_user1, field))

    def test_setitem(self):
        db = self.typical_db()
        mac_id = "quattrl"
        db[mac_id]["is_verified"] = 1
        db[mac_id]["discord_name"] = "luigi"
        db[mac_id]["discord_id"] = "196045824881328129"
        got_user = db[mac_id]
        for field, val in got_user.items():
            self.assertEqual(val, getattr(self.test_user2, field))

    def test_contains(self):
        db = self.typical_db()
        self.assertIn("quattrl", db)
        self.assertNotIn("torvall", db)


# python3 -m unittest tests/test_database.py -v
if __name__ == '__main__':
    main()