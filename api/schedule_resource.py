from flask_restful import abort, Resource
from flask import jsonify
from data.db_session import create_session, global_init
from data.schedule import Schedule

global_init('db\\data.sqlite')


def not_found(schedule_id):
    session = create_session()
    data = session.query(Schedule).get(schedule_id)
    if not data:
        abort(404, message=f"Schedule {schedule_id} not found")


class ScheduleResource(Resource):
    def get(self, schedule_id):
        not_found(schedule_id)
        session = create_session()
        data = session.query(Schedule).filter(Schedule.id == Schedule).first()
        return jsonify(data.to_dict())


class ScheduleListResource(Resource):
    def get(self):
        session = create_session()
        data = session.query(Schedule).all()
        return jsonify({'schedule': [item.to_dict() for item in data]})