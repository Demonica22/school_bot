from .db_session import SqlAlchemyBase
from sqlalchemy import Column, Integer, String
from sqlalchemy_serializer.serializer import SerializerMixin


class Schedule(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'schedule'
    id = Column(Integer, autoincrement=True, primary_key=True)
    grade = Column(String)
    weekday = Column(String)
    schedule = Column(String)
