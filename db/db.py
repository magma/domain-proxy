from contextlib import contextmanager
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session as sqlalchemy_session
from typing import List

from db.models import Base, DBRequest, DBRequestState, DBRequestType
from db.types import RequestStates, RequestTypes

Session = sqlalchemy_session


class DB:
    """
    This class is responsible for handling database operations for all DP services.
    """

    def __init__(self, uri: str, encoding: str, echo: bool, future: bool):
        self.uri = uri
        self.echo = echo
        self.future = future

        self.engine = create_engine(
            uri, encoding=encoding, echo=echo, future=future)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self) -> Session:
        session = self.session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def initialize(self) -> None:
        with self.session_scope() as s:
            for _type in RequestTypes:
                if not s.query(DBRequestType).filter(DBRequestType.name == _type.value).first():
                    request_type = DBRequestType(name=_type.value)
                    s.add(request_type)
            for state in RequestStates:
                if not s.query(DBRequestState).filter(DBRequestState.name == state.value).first():
                    request_state = DBRequestState(name=state.value)
                    s.add(request_state)
            s.commit()

    def get_requests(self, request_type: str, request_state: str) -> List[DBRequest]:
        with self.session_scope() as s:
            r = s.query(DBRequest).join(DBRequestType, DBRequestState).filter(
                and_(
                    DBRequestType.name == request_type,
                    DBRequestState.name == request_state
                )
            )
            return r.all()
