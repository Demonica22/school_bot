from flask_restful import abort, Resource
from flask import jsonify
from data.db_session import create_session, global_init
from data.news import News

global_init('db\\data.sqlite')


def not_found(news_id):
    session = create_session()
    data = session.query(News).get(news_id)
    if not data:
        abort(404, message=f"News {news_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        not_found(news_id)
        session = create_session()
        data = session.query(News).filter(News.id == news_id).first()
        return jsonify(data.to_dict())


class NewsListResource(Resource):
    def get(self):
        session = create_session()
        data = session.query(News).all()
        return jsonify({'news': [item.to_dict() for item in data]})