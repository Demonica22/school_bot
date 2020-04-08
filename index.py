import uuid

from flask import Flask, redirect, render_template
from flask_login.utils import login_user, login_required, logout_user
from data.db_session import global_init, create_session
from data.users import Users
from flask_login import LoginManager, current_user
from forms.registration_form import RegistrationForm
from forms.login_form import LoginForm
import hashlib
from flask_restful import Api
from api.news_resource import NewsResource, NewsListResource
from api.schedule_resource import ScheduleResource, ScheduleListResource
from api.schedule_calls_resource import ScheduleCallsResource, ScheduleCallsListResource

app = Flask(__name__)
api = Api(app)

global_init('db/data.sqlite')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'

'''
api
'''

api.add_resource(NewsResource, '/api/get/news/<int:news_id>')
api.add_resource(NewsListResource, '/api/get/news')
api.add_resource(ScheduleResource, '/api/get/schedule/<int:schedule_id>')
api.add_resource(ScheduleListResource, '/api/get/schedule')
api.add_resource(ScheduleCallsResource, '/api/get/schedule_calls/<int:schedule_call_id>')
api.add_resource(ScheduleCallsListResource, '/api/get/schedule_calls')


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect('/')
    except BaseException as a:
        return redirect("/login")


@app.route('/')
def start():
    return redirect('/main')


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(Users).get(user_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    def check_registration(form):
        session = create_session()
        if session.query(Users).filter(Users.email == form.email.data).first():
            return 'На этот email уже был создан аккаунт'
        if form.repeat_password.data != form.password.data:
            return 'Пароли не совпадают'
        return True

    def add_data(form):
        session = create_session()
        user = Users()
        user.email = form.email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.password = hash_password(form.password.data)
        session.add(user)
        session.commit()

    if current_user.is_authenticated:
        return redirect('/')

    form = RegistrationForm()
    form.hidden_tag()
    if form.validate_on_submit():
        if not check_registration(form):
            return render_template('registration_form.html', form=form, message=check_registration(form))
        add_data(form)
        return redirect('/')
    return render_template('registration_form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    def check_login(form):
        session = create_session()
        if not session.query(Users).filter(Users.email == form.login_or_nickname.data).first() \
                and not session.query(Users).filter(Users.email == form.email.data).first():
            return 'Нет такого email'
        else:
            return 'Неправильный пароль'

    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    form.hidden_tag()

    if form.validate_on_submit():
        session = create_session()

        user = session.query(Users).filter(Users.email == form.email.data).first()
        if user and check_password(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')

        return render_template('login_form.html', form=form, message=check_login(form))

    return render_template('login_form.html', form=form)


@app.route('/main_page')
def main_page():
    session = create_session()
    session.query()
    return ''


if __name__ == '__main__':
    '''
    http://127.0.0.1:5000/
    '''
    app.run()
