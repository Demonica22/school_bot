from flask_restful import abort, Resource
from flask import jsonify
from data.db_session import create_session, global_init
from data.schedule_calls import ScheduleCalls

global_init('db\\data.sqlite')


def not_found(schedule_call_id):
    session = create_session()
    data = session.query(ScheduleCalls).get(schedule_call_id)
    if not data:
        abort(404, message=f"Schedule calls {schedule_call_id} not found")


class ScheduleCallsResource(Resource):
    def get(self, schedule_call_id):
        not_found(schedule_call_id)
        session = create_session()
        data = session.query(ScheduleCalls).filter(ScheduleCalls.id == schedule_call_id).first()
        return jsonify(data.to_dict())


class ScheduleCallsListResource(Resource):
    def get(self):
        session = create_session()
        data = session.query(ScheduleCalls).all()
        return jsonify({'schedule calls': [item.to_dict() for item in data]})