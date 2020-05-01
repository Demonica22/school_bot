import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import json
from bot.settings import TOKEN, COM_ID
from requests import get
import time

WEEKDAYS = {"monday": "понедельник", "tuesday": "вторник", "wednesday": "среда", "thursday": "четверг",
            "friday": "пятница", "saturday": "суббота"}
vk_session = vk_api.VkApi(
    token=TOKEN)
longpoll = VkBotLongPoll(vk_session, COM_ID)
vk = vk_session.get_api()
action = ""
cur_requests = {}


def send_weekdays():
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
    vk.messages.send(user_id=event.obj.message['from_id'],
                     message="Здравствуйте, выберите один из предложенных вариантов дальнейшей работы",
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
        print(event)
        print(cur_requests)
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
                    for i in range(-3, 0, 1):
                        message = ""
                        message += f'{news[i]["title"]}\n'
                        message += news[i]["data"] + "\n"
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=message,
                                         random_id=random.randint(0, 2 ** 64))
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
                if cur_requests[event.obj.message['from_id']]["action"] == "schedule":
                    if "grade" not in cur_requests[event.obj.message['from_id']]:
                        cur_requests[event.obj.message['from_id']]["grade"] = "".join(message).lower()
                    try:
                        all_schedules = get('http://127.0.0.1:5000/api/get/schedule').json()["schedule"]
                        if cur_requests[event.obj.message['from_id']]["grade"].lower() in [item["grade"].lower() for
                                                                                           item in all_schedules]:
                            needed = list(
                                filter(
                                    lambda schedule: schedule["weekday"] == cur_requests[event.obj.message['from_id']][
                                        "weekday"].lower() and schedule[
                                                         "grade"] == cur_requests[event.obj.message['from_id']][
                                                         "grade"].lower(),
                                    all_schedules))[0]
                            message = ""
                            for i in range(1, len(needed["schedule"].split(", ")) + 1):
                                message += f"{i}. {needed['schedule'].split(', ')[i - 1]}\n"
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=message,
                                             random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message="Класс не найден или расписания не существует.",
                                             random_id=random.randint(0, 2 ** 64))
                            send_weekdays()
                    except Exception as x:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"Ошибка {x}\nКласс не найден или расписания не существует.",
                                         random_id=random.randint(0, 2 ** 64))
                        send_weekdays()
                elif cur_requests[event.obj.message['from_id']]["action"] == "schedule_calls":
                    if "grade" not in cur_requests[event.obj.message['from_id']]:
                        cur_requests[event.obj.message['from_id']]["grade"] = "".join(message).lower()
                    try:
                        all_schedules = get('http://127.0.0.1:5000/api/get/schedule_calls').json()["schedule_calls"]
                        if cur_requests[event.obj.message['from_id']]["grade"].lower() in [item["grade"].lower() for
                                                                                           item in all_schedules]:
                            needed = list(
                                filter(
                                    lambda schedule: schedule["weekday"] ==
                                                     cur_requests[event.obj.message['from_id']][
                                                         "weekday"].lower() and schedule[
                                                         "grade"] == cur_requests[event.obj.message['from_id']][
                                                         "grade"].lower(),
                                    all_schedules))[0]
                            message = ""
                            for i in range(1, len(needed["schedule_calls"].split(", ")) + 1):
                                message += f"{i}. {needed['schedule_calls'].split(', ')[i - 1]}\n"
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message=message,
                                             random_id=random.randint(0, 2 ** 64))
                        else:
                            vk.messages.send(user_id=event.obj.message['from_id'],
                                             message="Класс не найден или расписания не существует.",
                                             random_id=random.randint(0, 2 ** 64))
                            send_weekdays()
                    except Exception as x:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"Ошибка {x}\nКласс не найден или расписания не существует.",
                                         random_id=random.randint(0, 2 ** 64))
                        send_weekdays()
