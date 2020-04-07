from .db_session import SqlAlchemyBase
from sqlalchemy_serializer.serializer import SerializerMixin
from sqlalchemy import Column, Integer, Time


class ScheduleCalls(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'schedule_calls'
    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(Time)
