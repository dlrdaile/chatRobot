from .actor import Actor
from .env import Env
from .zhipuModel import Chat
from core.logger import logger
from collections import defaultdict
import time as time_module
from collections import deque


class Robot:
    def __init__(self, client_id: str, contact_id: str, chatClient: Chat, env: Env):
        self.chatClient = chatClient
        self.actor = Actor(self.chatClient)
        self.env = env
        self.client_id = client_id
        self.contact_id = contact_id
        self.time = 0
        self.t = 0
        self.max_times = 30
        self.activate_time = time_module.time()
        self.send_message_queue = {}


    async def run(self, content):
        message = ""
        time_s = '8:{:02d}'.format(self.time)
        end = 0
        print(time_s)
        if self.time > 0:
            self.actor.user_input(content)
        while True:
            self.activate_time = time_module.time()
            t, message = await self.actor.act(time_s)
            if t == 'A':
                self.time += 1
                break
            else:
                action = message
                response, act_time, end = await self.env.act(action)
                action[2] = response.replace('徐天行', '你')
                self.actor.add_action(action)
                self.time += act_time
                if self.time >= self.max_times or end > 0:
                    message = "对话结束"
                    break
        time_s = '8:{:02d}'.format(self.time)
        if self.time >= self.max_times:
            self.actor.reset()
            self.env.new_loop()
            self.time = 0
            end = 2
            print("=========================== Boom =============================")
        return message, time_s, end


class RobotManager:
    def __init__(self):
        self.robots = defaultdict(dict)

    def get_robot(self, client_id: str, contact_id: str):
        try:
            return self.robots[client_id].get(contact_id, None)
        except Exception as e:
            logger.warning(f"获取机器人失败，原因：{e}")
            return None

    def add_robot(self, client_id: str, contact_id: str, api_key: str):
        try:
            client_robot = self.robots[client_id].get(contact_id, {})
            if client_robot == {} or client_robot is None:
                chatClient = Chat(api_key)
                env = Env(chatClient)
                self.robots[client_id][contact_id] = {'chatClient': chatClient, 'env': env,
                                                      'robot': Robot(client_id, contact_id, chatClient, env)}
            else:
                if client_robot.get('chatClient', None) is None:
                    chatClient = Chat(api_key)
                    self.robots[client_id][contact_id]['chatClient'] = chatClient
                if client_robot.get('env', None) is None:
                    chatClient = self.robots[client_id][contact_id]['chatClient']
                    env = Env(chatClient)
                    self.robots[client_id][contact_id]['env'] = env
                if client_robot.get('robot', None) is None:
                    chatClient = self.robots[client_id][contact_id]['chatClient']
                    env = self.robots[client_id][contact_id]['env']
                    self.robots[client_id][contact_id]['robot'] = Robot(client_id, contact_id, chatClient, env)
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

    def cleanNoUseRobot(self):
        remove_contact_ids = []
        for client_id, robots in self.robots.items():
            for contact_id, robot in robots.items():
                if time_module.time() - robot['robot'].activate_time > 10 * 60:
                    remove_contact_ids.append((client_id, contact_id))

        for client_id, contact_id in remove_contact_ids:
            self.remove_robot(client_id, contact_id)
            logger.info(f"清理无用机器人：{client_id} {contact_id}")
            if len(self.robots[client_id]) == 0:
                self.robots.pop(client_id)
                logger.info(f"清理无用机器人：{client_id}")
