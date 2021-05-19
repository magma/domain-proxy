import unittest
import testing.postgresql

from db.db import DB, Session
from db.models import Base
from radio_controller.config import TestConfig

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


class DBTestCase(unittest.TestCase):
    postgresql: testing.postgresql.Postgresql

    @classmethod
    def setUpClass(cls) -> None:
        cls.postgresql = Postgresql()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.postgresql.stop()

    def get_config(self):
        config = TestConfig()
        config.SQLALCHEMY_DB_URI = self.postgresql.url()
        return config

    def setUp(self):
        config = self.get_config()
        self.db = DB(
            uri=config.SQLALCHEMY_DB_URI,
            encoding=config.SQLALCHEMY_DB_ENCODING,
            echo=config.SQLALCHEMY_ECHO,
            future=config.SQLALCHEMY_FUTURE
        )
        self.session = Session()
        Base.metadata.bind = self.db.engine
        Base.metadata.create_all()

    def tearDown(self):
        self.session.rollback()
        self.session.close()
        Base.metadata.drop_all()
