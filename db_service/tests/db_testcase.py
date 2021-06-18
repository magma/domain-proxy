import unittest

import testing.postgresql
from sqlalchemy import create_engine

from db_service.config import TestConfig
from db_service.models import Base
from db_service.session_manager import Session

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
        self.engine = create_engine(
            url=config.SQLALCHEMY_DB_URI,
            encoding=config.SQLALCHEMY_DB_ENCODING,
            echo=config.SQLALCHEMY_ECHO,
            future=config.SQLALCHEMY_FUTURE
        )
        self.session = Session()
        Base.metadata.bind = self.engine
        Base.metadata.create_all()

    def tearDown(self):
        self.session.rollback()
        self.session.close()
        Base.metadata.drop_all()
