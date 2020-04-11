import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import json
from bot.settings import TOKEN, COM_ID
from requests import get
import time

vk_session = vk_api.VkApi(
    token=TOKEN)
longpoll = VkBotLongPoll(vk_session, COM_ID)
vk = vk_session.get_api()
action = ""
for event in longpoll.listen():
    print(event.type)
    if event.type == VkBotEventType.MESSAGE_NEW:
        if "payload" in event.object["message"]:
            if eval(event.object["message"]["payload"])["command"] == "start":
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Здравствуйте, выберите один из предложенных вариантов дальнейшей работы",
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=json.dumps({"one_time": False, "buttons": [
                                     [{"action": {"type": "text", "label": "Расписание",
                                                  'payload': '{"command":"schedule"}'},
                                       "color": "negative"}, {"action": {"type": "text", "label": "Расписание звонков",
                                                                         'payload': '{"command":"schedule_calls"}'},
                                                              "color": "negative"}],
                                     [{"action": {"type": "text", "label": "Новости", 'payload': '{"command":"news"}'},
                                       "color": "negative"}
                                      ]]}))
            elif eval(event.object["message"]["payload"])["command"] == "schedule":
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Введите свой класс с буквой через пробел(Например: 7 А)",
                                 random_id=random.randint(0, 2 ** 64))
                action = "schedule"
            elif eval(event.object["message"]["payload"])["command"] == "schedule_calls":
                all_schedules = get('http://127.0.0.1:5000/api/get/schedule_calls').json()["schedule calls"]
                needed = list(
                    filter(lambda schedule: schedule["weekday"] == time.strftime("%A", time.strptime(time.asctime())).lower(), all_schedules))[0]
                message = ""
                for i in range(1, len(needed["schedule"].split(", ")) + 1):
                    message += f"{i}. {needed['schedule'].split(', ')[i - 1]}\n"
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=message,
                                 random_id=random.randint(0, 2 ** 64))
        else:
            message = event.object["message"]["text"].strip("\n").strip().split()
            if len(message) != 2:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Данные некорректны, введите свой класс еще раз",
                                 random_id=random.randint(0, 2 ** 64))
            else:
                if 1 <= int(message[0]) <= 11:
                    weekday = time.strftime("%A", time.strptime(time.asctime()))
                    if action == "schedule":
                        all_schedules = get('http://127.0.0.1:5000/api/get/schedule').json()["schedule"]
                        if "".join(message).lower() in [item["grade"].lower() for item in all_schedules]:
                            needed = list(
                                filter(lambda schedule: schedule["weekday"] == weekday.lower() and schedule[
                                    "grade"] == "".join(message).lower(),
                                       all_schedules))[0]
                            message = ""
                            for i in range(1, len(needed["schedule"].split(", ")) + 1):
                                message += f"{i}. {needed['schedule'].split(', ')[i - 1]}\n"
                    else:
                        message = "Данные некорректны или такого класса нет, введите его еще раз"

                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=message,
                                     random_id=random.randint(0, 2 ** 64))
                else:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Данные некорректны, введите свой класс еще раз",
                                     random_id=random.randint(0, 2 ** 64))
