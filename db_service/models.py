from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    payload = Column(JSON)

    state = relationship("DBRequestState", back_populates="requests")
    type = relationship("DBRequestType", back_populates="requests")
    response = relationship("DBResponse", back_populates="request")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
               f"type_id='{self.type_id}', " \
               f"state_id='{self.state_id}', " \
               f"cbsd_id='{self.cbsd_id}' " \
               f"payload='{self.payload}')>"


class DBResponse(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("request.id"))
    response_code = Column(Integer, nullable=False)
    payload = Column(JSON)

    request = relationship("DBRequest", back_populates="response")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}', " \
               f"request_id='{self.request_id}', " \
               f"response_code='{self.response_code}', " \
               f"payload='{self.payload}')>"
