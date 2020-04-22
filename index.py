import uuid

from flask import Flask, redirect, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from flask_login.utils import login_user, login_required, logout_user
from data.db_session import global_init, create_session
from data.users import Users
from flask_login import LoginManager, current_user
from forms.registration_form import RegistrationForm
from forms.login_form import LoginForm
from forms.add_news_form import AddNewsForm
import hashlib
from flask_restful import Api
from api.news_resource import NewsResource, NewsListResource
from api.schedule_resource import ScheduleResource, ScheduleListResource
from api.schedule_calls_resource import ScheduleCallsResource, ScheduleCallsListResource
from data.news import News
from data.schedule import Schedule
from wtforms.validators import DataRequired
import datetime
import os

app = Flask(__name__)
api = Api(app)

global_init('db/data.sqlite')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
home_dir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(home_dir, "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
IMAGES = {'png', 'jpg', 'jpeg', 'gif'}
VIDEOS = {'webm', 'mp3', 'mp4'}
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


def add_data(form, news):
    '''используется для добавления данных новостей в базу'''
    news.title = form.title.data
    news.data = form.data.data
    news.date_post = datetime.datetime.now()

    if not form.files.data[0].__nonzero__():
        return news

    # if not form.files.data[0].content_type == 'application/octet-stream':
    #     return news

    news.files = []

    for file in form.files.data:
        if os.listdir('uploads') == []:
            with open('uploads\\next_id.txt', 'w') as txt:
                txt.write('0')
        id = int(open('uploads\\next_id.txt').read())
        news.files.append(f'{id}.{file.filename.split(".")[-1]}')
        open('uploads\\next_id.txt', 'w').write(str(id + 1))
        file.save(f'uploads\\{id}.{file.filename.split(".")[-1]}')
    news.files = ';'.join(news.files)
    return news


@app.route('/news/add', methods=['GET', 'POST'])
def add_news():
    if not current_user.is_authenticated:
        return redirect('/login')

    if current_user.roles.name != 'admin':
        return redirect('/')

    form = AddNewsForm()
    form.hidden_tag()
    if form.validate_on_submit():
        session = create_session()
        news = add_data(form, News())
        session.add(news)
        session.commit()

    return render_template('add_news_form.html', form=form)


@app.route('/news/edit/<int:id>', methods=['GET', 'POST'])
def edit_news(id):
    if not current_user.is_authenticated:
        return redirect('/login')

    if current_user.roles.name != 'admin':
        return redirect('/')

    form = AddNewsForm()
    form.hidden_tag()

    session = create_session()
    news = session.query(News).filter(News.id == id).first()
    form.data.data = news.data
    files = news.files

    if form.validate_on_submit():
        news = add_data(form, news)
        if news.files == '':
            news.files = files
        session.commit()
        return redirect('/news')

    return render_template('add_news_form.html', form=form, data=news.to_dict())


@app.route('/news/delete/<int:id>')
def delete_news(id):
    if not current_user.is_authenticated:
        return redirect('/login')

    if current_user.roles.name != 'admin':
        return redirect('/')

    session = create_session()
    session.query(News).filter(News.id == id).delete()
    session.commit()

    return redirect('/news')



@app.route('/schedule/lessons/add', methods=['GET', 'POST'])
def add_schedule():
    session = create_session()

    def add_data():
        schedule = session.query(Schedule).filter(Schedule.weekday == request.form['weekday'],
                                                  Schedule.grade == (request.form['number_grade'] + request.form[
                                                      'letter_grade'])).first()
        flag = True
        if not schedule:
            flag = False
            schedule = Schedule()
        schedule.grade = request.form['number_grade'] + request.form['letter_grade'].lower()
        schedule.weekday = request.form['weekday']
        schedule.schedule = ''.join(request.form['schedule'].split('\r'))
        if not flag:
            session.add(schedule)
        session.commit()

    def check():
        errors = dict()
        message = 'Форма не заполнена'
        if request.form['number_grade'] == "":
            errors['number_grade'] = message

        if request.form['letter_grade'] == "":
            errors['letter_grade'] = message

        if request.form['schedule'] == "":
            errors['schedule'] = message

        if len(request.form['letter_grade']) > 1:
            errors['letter_grade'] = 'В этом поле должен быть только один символ'
        if not request.form['letter_grade'].isalpha():
            errors['letter_grade'] = 'В этом поле должна быть буква'
        if not request.form['number_grade'].isdigit():
            errors['number_grade'] = 'В этом поле должно быть число'

        return errors

    if not current_user.is_authenticated:
        return redirect('/login')

    if current_user.roles.name != 'admin':
        return redirect('/schedule/lessons')

    if request.method == 'POST':
        errors = check()
        if not errors:
            add_data()
            return redirect('/schedule/lessons')
        return render_template('add_schedule_form.html', errors=errors)

    return render_template('add_schedule_form.html', errors=None)


@app.route('/news')
def news():
    session = create_session()
    data = []
    for el in session.query(News).all():
        data.append(
            {
                'id': el.id,
                'title': el.title,
                'data': el.data,
                'date': el.date_post,
                'images': list(filter(lambda x: x.split('.')[-1] in IMAGES, el.files.split(';'))),
                'videos': list(filter(lambda x: x.split('.')[-1] in VIDEOS, el.files.split(';'))),
                'files': list(filter(lambda x: x.split('.')[-1] not in VIDEOS
                                               and x.split('.')[-1] not in IMAGES, el.files.split(';')))
            }
        )
    return render_template('news.html', data=data, max_index=len(data))


@app.route('/uploads/<file>')
def uploaded_file(file):
    return send_from_directory(app.config["UPLOAD_FOLDER"], file)


@app.route('/get/image/<file>')
def get_image(file):
    return open(f'uploads/{file}', "rb").read()


@app.route('/video/<file>')
def watch_video(file):
    return render_template('video.html', video=file)


@app.route('/get/video/<file>')
def get_video(file):
    return open(f'uploads/{file}', 'rb').read()


@app.route('/schedule/lessons', methods=['GET', 'POST'])
def menu_schedule_lessons():
    def sort_grades():
        data = session.query(Schedule).all()
        list_grades = set()
        for el in data:
            list_grades.add(el.grade)
        list_grades = list(map(lambda x: (int(x[:-1]), x[-1]), list_grades))
        list_grades.sort(key=lambda x: x[1], reverse=True)
        list_grades.sort(key=lambda x: x[0])
        list_grades.reverse()
        list_grades = list(map(lambda x: str(x[0]) + x[1], list_grades))
        return list_grades

    session = create_session()
    if request.method == 'POST':
        return redirect(f'/schedule/lessons/{request.form["select_grade"]}')

    return render_template('menu_schedule_lessons.html', list_grades=sort_grades())


@app.route('/schedule/lessons/<string:grade>')
def schedule_lessons(grade):
    LIST_WEEKDAYS = [
        'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье'
    ]
    if not current_user.is_authenticated:
        return redirect('/login')
    session = create_session()
    data = session.query(Schedule).filter(Schedule.grade == grade).all()
    data.sort(key=lambda x: LIST_WEEKDAYS.index(x.weekday))

    return render_template('schedule_lessons.html', grade=grade, data=data)


@app.route('/schedule/lessons/<string:grade>/<string:weekday>/edit', methods=['GET', 'POST'])
def edit_schedule_lessons(grade, weekday):
    session = create_session()
    schedule = session.query(Schedule).filter(Schedule.grade == grade, Schedule.weekday == weekday).first()

    if request.method == 'POST':
        if request.form['schedule'].split() == []:
            error = {'schedule': 'Форма пуста'}
            return render_template('edit_schedule_lessons.html', data=schedule.schedule, errors=error)
        schedule.schedule = request.form['schedule']
        session.commit()
        return redirect(f'/schedule/lessons/{grade}')

    return render_template('edit_schedule_lessons.html', data=schedule.schedule, errors=None)


if __name__ == '__main__':
    '''
    http://127.0.0.1:5000/
    '''
    app.run()
