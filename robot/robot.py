from .actor import Actor
from .env import Env
from .zhipuModel import Chat
from typing import Dict
from core.logger import logger


class Robot:
    def __init__(self, client_id: str, contact_id: str, api_key: str):
        self.chatClient = Chat(api_key)
        self.actor = Actor(self.chatClient)
        self.env = Env(self.chatClient)
        self.client_id = client_id
        self.contact_id = contact_id
        self.time = 0
        self.t = 0
        self.max_times = 30

    def run(self, content):
        message = None
        time_s = '8:{:02d}'.format(self.time)
        end = 0
        print(time_s)
        if self.time > 0:
            self.actor.user_input(content)

        while True:
            t, message = self.actor.act(time_s)
            if t == 'A':
                self.time += 1
                break
            else:
                action = message
                response, act_time, end = self.env.act(action)
                action[2] = response.replace('徐天行', '你')
                self.actor.add_action(action)
                self.time += act_time
                if self.time >= self.max_times or end > 0:
                    message = None
                    break

        if self.time >= self.max_times:
            self.actor.reset()
            self.env.new_loop()
            self.time = 0
            end = 2
            print("=========================== Boom =============================")

        time_s = '8:{:02d}'.format(self.time)
        return message, time_s, end


class RobotManager:
    def __init__(self):
        self.robots: Dict[str, Dict[str, Robot]] = {}

    def get_robot(self, client_id: str, contact_id: str):
        try:
            return self.robots[client_id].get(contact_id, None)
        except Exception as e:
            logger.warning(f"获取机器人失败，原因：{e}")
            return None

    def add_robot(self, client_id: str, contact_id: str, api_key: str):
        try:
            client_robot = self.robots.get(client_id, None)
            if client_robot is None:
                self.robots[client_id] = {contact_id: Robot(client_id, contact_id, api_key)}
            else:
                if client_robot.get(contact_id, None) is None:
                    self.robots[client_id][contact_id] = Robot(client_id, contact_id, api_key)
        except Exception as e:
            logger.warning(f"添加机器人失败，原因：{e}")

    def remove_robot(self, client_id: str, contact_id: str):
        try:
            self.robots[client_id].pop(contact_id)
        except Exception as e:
            logger.warning(f"删除机器人失败，原因：{e}")

    def remove_all_robot(self, client_id: str):
        try:
            self.robots.pop(client_id)
        except Exception as e:
            logger.warning(f"删除机器人失败，原因：{e}")
