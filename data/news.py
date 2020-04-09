from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy_serializer.serializer import SerializerMixin
from sqlalchemy import orm, Column, Integer, String, DateTime


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'
    id = sqlalchemy.Column(Integer, autoincrement=True, primary_key=True)
    data = Column(String)
    title = Column(String)
    images = Column(String)
    videos = Column(String)
    user_id = Column(Integer, sqlalchemy.ForeignKey("users.id"))
    date_post = Column(DateTime)
    user = orm.relation('Users')