from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DBRequestType(Base):
    __tablename__ = "request_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<RequestType(id='{self.id}', name='{self.name}')>"

class DBRequestState(Base):
    __tablename__ = "request_state"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<RequestState(id='{self.id}', name='{self.name}')>"

class DBRequest(Base):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("request_type.id"))
    state_id = Column(Integer, ForeignKey("request_state.id"))
    cbsd_id = Column(String, nullable=False)
    payload = Column(JSON)

    def __repr__(self):
        return f"<Request(id='{self.id}', type_id='{self.type_id}', state_id='{self.state_id}', cbsd_id='{self.cbsd_id}' payload='{self.payload}')>"

class DBResponse(Base):
    __tablename__ = "response"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("request.id"))
    response_code = Column(Integer, nullable=False)
    payload = Column(JSON)

    def __repr__(self):
        return f"<Response(id='{self.id}', request_id='{self.request_id}', response_code='{self.response_code}', payload='{self.payload}')>"
