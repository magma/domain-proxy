import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

Base = declarative_base()


class DBRequestType(Base):
    __tablename__ = "request_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    requests = relationship("DBRequest", back_populates="type")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', name='{self.name}')>"


class DBRequestState(Base):
    __tablename__ = "request_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    requests = relationship("DBRequest", back_populates="state")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', name='{self.name}')>"


class DBRequest(Base):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey("request_type.id"))
    state_id = Column(Integer, ForeignKey("request_state.id"))
    cbsd_id = Column(String, nullable=False)
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=now())
    updated_date = Column(DateTime(timezone=True), server_default=now(), onupdate=now())
    payload = Column(JSON)

    state = relationship("DBRequestState", back_populates="requests")
    type = relationship("DBRequestType", back_populates="requests")
    response = relationship("DBResponse", back_populates="request")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
            f"type='{self.type.name}', " \
            f"state='{self.state.name}', " \
            f"cbsd_id='{self.cbsd_id}' " \
            f"created_date='{self.created_date}' " \
            f"updated_date='{self.updated_date}' " \
            f"payload='{self.payload}')>"


class DBResponse(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("request.id"))
    grant_id = Column(Integer, ForeignKey("grant.id"), nullable=True)
    response_code = Column(Integer, nullable=False)
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=now())
    payload = Column(JSON)

    request = relationship("DBRequest", back_populates="response")
    grant = relationship("DBGrant", back_populates="responses")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
            f"request_id='{self.request_id}', " \
            f"response_code='{self.response_code}', " \
            f"created_date='{self.created_date}' " \
            f"payload='{self.payload}')>"

class DBGrantState(Base):
    __tablename__ = "grant_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    grants = relationship("DBGrant", back_populates="state")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
            f"name='{self.name}'>"

class DBGrant(Base):
    __tablename__ = "grant"
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(Integer, ForeignKey("grant_state.id"))
    cbsd_id = Column(String, nullable=False)
    grant_id = Column(String, nullable=False)
    grant_expire_time = Column(DateTime(timezone=True))
    transmit_expire_time = Column(DateTime(timezone=True))
    heartbeat_interval = Column(Integer)
    channel_type = Column(String)
    created_date = Column(DateTime(timezone=True), nullable=False, server_default=now())
    updated_date = Column(DateTime(timezone=True), server_default=now(), onupdate=now())

    state = relationship("DBGrantState", back_populates="grants")
    responses = relationship("DBResponse", back_populates="grant")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
            f"state='{self.state.name}', " \
            f"cbsd_id='{self.cbsd_id}', " \
            f"grant_id='{self.grant_id}', " \
            f"grant_expire_time='{self.grant_expire_time}', " \
            f"transmit_expire_time='{self.transmit_expire_time}', " \
            f"heartbeat_interval='{self.heartbeat_interval}', " \
            f"channel_type='{self.channel_type}', " \
            f"created_date='{self.created_date}' " \
            f"updated_date='{self.updated_date}')>"
