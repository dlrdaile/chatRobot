import time as time_module

from core.logger import logger
from schema.websocket.ChatItemModel import ApiKeyModel
from .actor import Actor
from .env import Env
from .zhipuModel import Chat
from typing import Optional
from pydantic import BaseModel


class ContextResponseModel(BaseModel):
    message: str
    time_s: str
    end: int
    robot_time: int


class Robot:
    def __init__(self, client_id: str, chatClient: Chat):
        self.client_id = client_id
        self.env = Env()
        self.chat_client = chatClient
        self.robot_context = {}
        self.activate_time = time_module.time()
        self.send_message_queue = {}

    def add_context(self, contact_id: str):
        self.robot_context[contact_id] = RobotContext(self)
        return self.robot_context[contact_id]

    async def run(self, contact_id: str, content: str) -> ContextResponseModel:
        try:
            self.activate_time = time_module.time()
            context = self.robot_context.get(contact_id, None)
            if context is None:
                context = self.add_context(contact_id)
            result = await context.run(content, self.chat_client)
        except Exception as e:
            error_info = f"机器人运行失败，原因：{e}"
            logger.error(error_info)
            raise Exception(error_info)
        else:
            self.activate_time = time_module.time()
        return result


class RobotContext:
    def __init__(self, robot: Robot):
        self.actor = Actor()
        self.robot = robot
        self.time = 0
        self.t = 0
        self.max_times = 30
        self.activate_time = time_module.time()

    async def run(self, content, chatClient: Chat) -> ContextResponseModel:
        self.activate_time = time_module.time()
        message = ""
        time_s = '8:{:02d}'.format(self.time)
        end = 0
        print(time_s)
        if self.time > 0:
            self.actor.user_input(content)
        while True:
            self.activate_time = time_module.time()
            t, message = await self.actor.act(time_s, chatClient)
            if t == 'A':
                self.time += 1
                break
            else:
                action = message
                response, act_time, end = await self.robot.env.act(action, chatClient)
                action[2] = response.replace('徐天行', '你')
                self.actor.add_action(action)
                self.time += act_time
                if self.time >= self.max_times or end > 0:
                    message = "对话结束"
                    break
        time_s = '8:{:02d}'.format(self.time)
        if self.time >= self.max_times:
            self.actor.reset()
            self.robot.env.new_loop()
            self.time = 0
            end = 2
            print("=========================== Boom =============================")
        return ContextResponseModel(message=message, time_s=time_s, end=end, robot_time=self.time)


class RobotManager:
    robots = {}

    @classmethod
    async def create_chat_client(cls, requestModel: ApiKeyModel):
        api_key = requestModel.api_key
        chat_client = Chat(api_key, requestModel.llm_platform, requestModel.llm_model)
        res = await chat_client.chat("你好")
        robot = cls.get_robot(requestModel.client_id)
        if robot is None:
            robot = cls.add_robot(requestModel.client_id)
        robot.chat_client = chat_client
        return res

    @classmethod
    def get_robot(cls, client_id: str) -> Optional[Robot]:
        return cls.robots.get(client_id, None)

    @classmethod
    def add_robot(cls, client_id: str, chatClient: Chat = None) -> Optional[Robot]:
        try:
            robot = cls.get_robot(client_id)
            if robot is None:
                cls.robots[client_id] = Robot(client_id, chatClient)
        except Exception as e:
            logger.warning(f"添加机器人失败，原因：{e}")
        return cls.get_robot(client_id)

    @classmethod
    def remove_robot(cls, client_id: str) -> bool:
        try:
            cls.robots.pop(client_id)
            return True
        except Exception as e:
            logger.warning(f"删除机器人失败，原因：{e}")
        return False

    @classmethod
    def cleanNoUseRobot(cls):
        now = time_module.time()
        remove_contact_ids = []
        remove_client_ids = []
        for client_id, robot in cls.robots.items():
            if now - robot.activate_time > 10 * 60:
                remove_client_ids.append(client_id)
                continue
            for contact_id, robot_context in robot.robot_context.items():
                if now - robot_context.activate_time > 5 * 60:
                    remove_contact_ids.append((client_id, contact_id))
        for client_id in remove_client_ids:
            cls.remove_robot(client_id)
            logger.info(f"清理无用机器人：{client_id}")
        for client_id, contact_id in remove_contact_ids:
            robot = cls.get_robot(client_id)
            if robot is not None:
                try:
                    robot.robot_context.pop(contact_id)
                    logger.info(f"清理无用机器人：{client_id} {contact_id}")
                except:
                    logger.warning(f"清理无用机器人失败：{client_id} {contact_id}")
