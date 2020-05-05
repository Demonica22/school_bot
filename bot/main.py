import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import json
from bot.settings import TOKEN, COM_ID, NEWS_COUNT
from requests import get

WEEKDAYS = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среда", "thursday": "четверг",
            "friday": "пятница", "saturday": "суббота"}
vk_session = vk_api.VkApi(
    token=TOKEN)
longpoll = VkBotLongPoll(vk_session, COM_ID)
vk = vk_session.get_api()
# словарь из текущих запросов пользователя ( {user_id: {"action": "action_name","grade":"grade_name"}} )
cur_requests = {}


def send_weekdays():
    """
        Функция отправки меню с днями недели для пользователя ( in-line keyboard)
        """
    vk.messages.send(user_id=event.obj.message['from_id'],
                     message="Выберите день недели для просмотра расписания",
                     random_id=random.randint(0, 2 ** 64),
                     keyboard=json.dumps({"one_time": True, "buttons": [
                         [{"action": {"type": "text", "label": "Понедельник",
                                      'payload': '{"command":"week_day"}'
                                      },
                           "color": "negative"},
                          {"action": {"type": "text", "label": "Вторник",
                                      'payload': '{"command":"week_day"}'
                                      },
                           "color": "negative"},
                          {"action": {"type": "text", "label": "Среда", 'payload': '{"command":"week_day"}'
                                      },
                           "color": "negative"}], [
                             {"action": {"type": "text", "label": "Четверг",
                                         'payload': '{"command":"week_day"}'
                                         },
                              "color": "negative"},
                             {"action": {"type": "text", "label": "Пятница",
                                         'payload': '{"command":"week_day"}'
                                         },
                              "color": "negative"}
                         ], [{"action": {"type": "text", "label": "Вернуться в меню",
                                         'payload': '{"command":"menu"}'
                                         },
                              "color": "positive"}]]}))


def send_menu():
    """
    Функция отправки основного меню для пользователя ( in-line keyboard)
    """
    vk.messages.send(user_id=event.obj.message['from_id'],
                     message="Выберите один из предложенных вариантов дальнейшей работы",
                     random_id=random.randint(0, 2 ** 64),
                     keyboard=json.dumps({"one_time": True, "buttons": [
                         [{"action": {"type": "text", "label": "Расписание",
                                      'payload': '{"command":"schedule"}'},
                           "color": "negative"}, {"action": {"type": "text", "label": "Расписание звонков",
                                                             'payload': '{"command":"schedule_calls"}'},
                                                  "color": "negative"}],
                         [{"action": {"type": "text", "label": "Новости", 'payload': '{"command":"news"}'},
                           "color": "negative"}
                          ]]}))


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        # Если сообщение отправлено с кнопки клавиатуры бота, т.е существует ключ "payload",
        # то обрабатываем запрос с помощью него
        if "payload" in event.object["message"]:
            if eval(event.object["message"]["payload"])["command"] == "start":
                send_menu()
            elif eval(event.object["message"]["payload"])["command"] == "schedule":
                # Начало обработки запроса на получение расписания уроков
                send_weekdays()
                cur_requests[event.obj.message['from_id']] = {"action": "schedule"}
            elif eval(event.object["message"]["payload"])["command"] == "schedule_calls":
                # Начало обработки запроса на получение расписания звонков
                send_weekdays()
                cur_requests[event.obj.message['from_id']] = {"action": "schedule_calls"}
            elif eval(event.object["message"]["payload"])["command"] == "week_day":
                # если после отправки дня недели выбрано действие расписания звонков, то класс запрашивать не нужно и
                # отправка расписания происходит сразу после получения сообщения о дне недели
                if cur_requests[event.obj.message['from_id']]["action"] == "schedule_calls":
                    cur_requests[event.obj.message['from_id']]["weekday"] = event.object["message"]["text"].strip(
                        "\n").strip().split()
                    try:
                        all_schedules = get('http://127.0.0.1:5000/api/get/schedule_calls').json()["schedule calls"]
                        needed = list(
                            filter(
                                lambda schedule: schedule["weekday"] ==
                                                 cur_requests[event.obj.message['from_id']][
                                                     "weekday"][0].lower(),
                                all_schedules))[0]
                        message = ""
                        for i in range(1, len(needed["schedule"].split("\n")) + 1):
                            message += "{}. {}\n".format(i, needed['schedule'].split('\n')[i - 1])
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=message,
                                         random_id=random.randint(0, 2 ** 64))
                        cur_requests[event.obj.message['from_id']] = {}
                        send_menu()
                    except Exception as x:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"Ошибка {x}\nКласс не найден или расписания не существует.",
                                         random_id=random.randint(0, 2 ** 64))
                        cur_requests[event.obj.message['from_id']] = {}
                        send_menu()
                else:
                    # Если же запрос не расписания звонков, то происходит запрос класса у пользователя и день недели
                    # записывается в словарь с ключем weekday

                    if event.obj.message['from_id'] not in cur_requests:
                        cur_requests[event.obj.message['from_id']] = {}
                    cur_requests[event.obj.message['from_id']]["weekday"] = event.object["message"]["text"].strip(
                        "\n").strip().split()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Введите свой класс c буквой через пробел (Например: 7 А)",
                                     random_id=random.randint(0, 2 ** 64))

            elif eval(event.object["message"]["payload"])["command"] == "news":
                try:
                    news = get('http://127.0.0.1:5000/api/get/news').json()["news"]
                    if news:
                        count = min(NEWS_COUNT, len(news))
                        for i in range(count, 0, 1):
                            message = ""
                            message += f'{news[i]["title"]}\n'
                            message += news[i]["data"] + "\n"
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=message,
                                             random_id=random.randint(0, 2 ** 64))
                    else:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="К сожалению, список новостей пуст",
                                         random_id=random.randint(0, 2 ** 64))
                    send_menu()

                except Exception as x:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Ошибка {x}\n",
                                     random_id=random.randint(0, 2 ** 64))
                    send_menu()
            elif eval(event.object["message"]["payload"])["command"] == "menu":
                send_menu()

        else:
            message = event.object["message"]["text"].strip("\n").strip().split()
            if event.obj.message['from_id'] in cur_requests:
                if "action" not in cur_requests[event.obj.message['from_id']]:
                    cur_requests[event.obj.message['from_id']]["action"] = None
                if cur_requests[event.obj.message['from_id']]["action"] == "schedule":
                    # Если действие - получение расписания (schedule) то происходит запрос к api и обрабатываются все
                    # полученные расписания, которые удовлетворяют запросу ( день недели и выбранный класс)
                    if "grade" not in cur_requests[event.obj.message['from_id']]:
                        cur_requests[event.obj.message['from_id']]["grade"] = "".join(message).lower()
                    try:
                        all_schedules = get('http://127.0.0.1:5000/api/get/schedule').json()["schedule"]
                        if cur_requests[event.obj.message['from_id']]["grade"].lower() in [item["grade"].lower() for
                                                                                           item in all_schedules]:
                            needed = list(
                                filter(
                                    lambda schedule: schedule["weekday"].lower() ==
                                                     cur_requests[event.obj.message['from_id']][
                                                         "weekday"][0].lower() and schedule[
                                                         "grade"] == cur_requests[event.obj.message['from_id']][
                                                         "grade"].lower(),
                                    all_schedules))[0]
                            message = ""
                            for i in range(1, len(needed["schedule"].split("\n")) + 1):
                                message += "{}. {}\n".format(i, needed['schedule'].split('\n')[i - 1])
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=message,
                                             random_id=random.randint(0, 2 ** 64))
                            send_menu()
                        else:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message="Класс не найден или расписания не существует.",
                                             random_id=random.randint(0, 2 ** 64))
                            cur_requests[event.obj.message['from_id']] = {}
                            send_menu()
                    except Exception as x:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"Ошибка {x}\nКласс не найден или расписания не существует.",
                                         random_id=random.randint(0, 2 ** 64))
                        cur_requests[event.obj.message['from_id']] = {}
                        send_menu()
