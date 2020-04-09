from .db_session import SqlAlchemyBase
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm


class Users(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    role_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("roles.id"), default=1)
    password = sqlalchemy.Column(sqlalchemy.String)
    roles = orm.relation('Roles')