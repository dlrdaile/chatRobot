"""
author:dlr123
date:2022年06月14日
"""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from core.logger import logger
from .common import ConnectionManager
from schema.websocket.SendDataModel import SendDataModel
from schema.websocket.ChatItemModel import ChatItemModel
from uuid import uuid4
from robot.robot import RobotManager

websocket_api = APIRouter(prefix='/ws')
manager = ConnectionManager()


class WebSocketFrameProcess:
    @staticmethod
    def get_data(data: SendDataModel) -> dict:
        res_data = data
        return res_data.model_dump()

    @classmethod
    async def process_frame_data(cls, data: dict, client_id: str, route: str):
        try:
            socketType = data.get('socketType', "")
            robot = RobotManager.get_robot(client_id)
            if robot is not None:
                for message_frame in robot.send_message_queue.values():
                    await manager.send_personal_json(message_frame, client_id, route)
                robot.send_message_queue = {}
            if socketType == 'heartBeat':
                await cls._process_heartBeat_frame_data(data, client_id, route)
            elif socketType == 'userInfo':
                await cls._process_chat_frame_data(data, client_id, route)
            elif socketType == 'createChatClient':
                await cls._process_createChatClient_frame_data(data, client_id, route)
            else:
                logger.warning(f'websocket接收到无法处理的数据,因为：{data}')
        except Exception as e:
            receive_data = SendDataModel(socketType="backFail", data=str(e))
            res_data = cls.get_data(receive_data)
            try:
                await manager.send_personal_json(res_data, client_id, route)
            except Exception as e:
                logger.error(f'websocket连接出错,因为：{e}')

    @classmethod
    async def _process_heartBeat_frame_data(cls, data: dict, client_id: str, route: str):
        receive_data = SendDataModel(**data)
        receive_data.data = 'pong'
        await manager.send_personal_json(receive_data.model_dump(), client_id, route)

    @classmethod
    async def _process_createChatClient_frame_data(cls, data: dict, client_id: str, route: str):
        receive_data = SendDataModel(**data)
        res = await RobotManager.create_chat_client(receive_data.data)
        receive_data = SendDataModel()
        receive_data.socketType = "successCreateClient"
        receive_data.data = res
        res_data = cls.get_data(receive_data)
        await manager.send_personal_json(res_data, client_id, route)

    @classmethod
    async def _process_chat_frame_data(cls, data: dict, client_id: str, route: str):
        receive_data = SendDataModel(**data)
        robot = RobotManager.get_robot(client_id)
        if robot is None:
            raise ValueError("请连接某个大模型应用")
        content = receive_data.data.content
        contact_id = receive_data.data.toContactId
        random_id = uuid4().hex
        result = await robot.run(contact_id, content)
        message = result.message
        if isinstance(message, str) or result.end != 0:
            receive_data.data = ChatItemModel(
                content=message if message is not None else "对话结束",
                sendTime=result.time_s,
                id=random_id,
                status="success",
                type="text",
                toContactId=receive_data.data.toContactId,
                fromUser={
                    "avatar": "https://dl-demo-test1.oss-cn-beijing.aliyuncs.com/myBlog/imgassets%2Fimg%2F2024%2F03%2F23%2F19-30-00-3e3888ea071cad811454261db447c0fe-fbb7c5f5807747ddbe57a1d1a395860-b73d21.png",
                    "displayName": "徐天行",
                    "id": receive_data.data.fromUser.id},
                time=result.robot_time,
                end=result.end
            )
            receive_data.socketType = "sendData"
            res_data = cls.get_data(receive_data)
            robot.send_message_queue = {random_id: res_data}
            await manager.send_personal_json(res_data, robot.client_id, route)
        if random_id in robot.send_message_queue:
            robot.send_message_queue.pop(random_id)


async def test_background():
    print('test_background')
    await asyncio.sleep(5)
    print('test_background end')


@websocket_api.websocket("/chat/{client_id}")
async def get_process_data(websocket: WebSocket, client_id: str):
    route = 'chat'
    await manager.connect(client_id, route, websocket)
    robot = RobotManager.get_robot(client_id)
    if robot is not None:
        for message_frame in robot.send_message_queue.values():
            await manager.send_personal_json(message_frame, client_id, route)
        robot.send_message_queue = {}
    try:
        while True:
            data = await websocket.receive_json()
            await WebSocketFrameProcess.process_frame_data(data, client_id, route)
    except WebSocketDisconnect as e:
        manager.disconnect(client_id, route)
        logger.error(f'websocket连接出错,因为：{e}')
    except Exception as e:
        logger.error(f'websocket数据处理异常,因为：{e}')
