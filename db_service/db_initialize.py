import importlib
import os

from sqlalchemy import create_engine

from db_service.config import Config
from db_service.models import DBGrantState, DBRequestState, DBRequestType
from db_service.session_manager import SessionManager
from mappings.types import GrantStates, RequestStates, RequestTypes


class DBInitializer:
    """
    This class is responsible for initializing the database with data.
    """
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def initialize(self) -> None:
        with self.session_manager.session_scope() as s:
            for _type in RequestTypes:
                if not s.query(DBRequestType).filter(DBRequestType.name == _type.value).first():
                    request_type = DBRequestType(name=_type.value)
                    s.add(request_type)
            for state in RequestStates:
                if not s.query(DBRequestState).filter(DBRequestState.name == state.value).first():
                    request_state = DBRequestState(name=state.value)
                    s.add(request_state)
            for state in GrantStates:
                if not s.query(DBGrantState).filter(DBGrantState.name == state.value).first():
                    grant_state = DBGrantState(name=state.value)
                    s.add(grant_state)
            s.commit()


def get_config() -> Config:
    app_config = os.environ.get('APP_CONFIG', 'db_service.config.ProductionConfig')
    config_module = importlib.import_module('.'.join(app_config.split('.')[:-1]))
    config_class = getattr(config_module, app_config.split('.')[-1])

    return config_class()


if __name__ == '__main__':
    config = get_config()
    db_engine = create_engine(
        url=config.SQLALCHEMY_DB_URI,
        encoding=config.SQLALCHEMY_DB_ENCODING,
        echo=config.SQLALCHEMY_ECHO,
        future=config.SQLALCHEMY_FUTURE
    )
    session_manager = SessionManager(db_engine=db_engine)
    initializer = DBInitializer(session_manager)
    initializer.initialize()
