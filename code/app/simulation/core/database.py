import logging
import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


class Database:

    def __init__(self, table_name='simulation'):
        self.logger = logging.getLogger(__name__)
        self.db_path = os.environ['DB_FILEPATH']
        self.db = TinyDB(
            self.db_path,
            storage=CachingMiddleware(JSONStorage)
        )
        self.table = self.db.table(table_name)

    def search(self, **args):
        return self.table.insert(args)

    def insert(self, **kwargs):
        return self.table.insert(kwargs)

    def query(self):
        return Query()

    def all(self):
        return self.table.all()
