from .db_session import SqlAlchemyBase
from sqlalchemy_serializer.serializer import SerializerMixin
from sqlalchemy import Column, Integer, String


class ScheduleCalls(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'schedule_calls'
    id = Column(Integer, autoincrement=True, primary_key=True)
    weekday = Column(String)
    schedule = Column(String)
