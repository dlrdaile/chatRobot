from .actor import Actor
from .env import Env
from typing import Dict
from core.logger import logger


class Robot:
    def __init__(self, client_id: str, contact_id: str):
        self.actor = Actor()
        self.env = Env()
        self.client_id = client_id
        self.contact_id = contact_id
        self.time = 0
        self.t = 0

    def run(self, content):
        message = None
        time_s = '8:{:02d}'.format(self.time)
        if self.t == 0:
            message = self.actor.act(time_s, 'message')

            self.actor.user_input(content)
            self.time += 1
        else:
            action = self.actor.act(time_s, 'action')
            response, act_time = self.env.act(action)
            action[2] = response.replace('徐天行', '你')
            self.actor.add_action(action)
            self.time += act_time
        self.t = 1 - self.t
        if self.time >= 20:
            self.actor.reset()
            self.env.new_loop()
            self.time = 0
            self.t = 0
            print("=========================== Boom =============================")
        return message, time_s


class RobotManager:
    def __init__(self):
        self.robots: Dict[str, Dict[str, Robot]] = {}

    def get_robot(self, client_id: str, contact_id: str):
        try:
            return self.robots[client_id].get(contact_id, None)
        except Exception as e:
            logger.warning(f"获取机器人失败，原因：{e}")
            return None

    def add_robot(self, client_id: str, contact_id: str):
        try:
            client_robot = self.robots.get(client_id, None)
            if client_robot is None:
                self.robots[client_id] = {contact_id: Robot(client_id, contact_id)}
            else:
                if client_robot.get(contact_id, None) is None:
                    self.robots[client_id][contact_id] = Robot(client_id, contact_id)
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
