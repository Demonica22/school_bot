from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String


class Roles(SqlAlchemyBase):
    __tablename__ = 'roles'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
