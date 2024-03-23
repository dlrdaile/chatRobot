"""
author:dlr123
date:2022年06月14日
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from core.logger import logger
from .common import ConnectionManager
from schema.websocket.SendDataModel import SendDataModel
from schema.websocket.ChatItemModel import ChatItemModel
from robot import ml_models
from uuid import uuid4
from robot.robot import RobotManager, Robot

websocket_api = APIRouter(prefix='/ws')
manager = ConnectionManager()
robotsManager = RobotManager()


def get_data(data: SendDataModel) -> dict:
    res_data = data
    return res_data.model_dump()


async def responseUser(receive_data: SendDataModel, robot: Robot, route: str):
    message, time_s = robot.run(receive_data.data.content)
    if isinstance(message, str):
        receive_data.data = ChatItemModel(
            content=message,
            sendTime=time_s,
            id=uuid4().hex,
            status="success",
            type="text",
            toContactId=receive_data.data.toContactId,
            fromUser={
                "avatar": "https://dl-demo-test1.oss-cn-beijing.aliyuncs.com/myBlog/imgassets%2Fimg%2F2024%2F03%2F23%2F19-30-00-3e3888ea071cad811454261db447c0fe-fbb7c5f5807747ddbe57a1d1a395860-b73d21.png",
                "displayName": "徐天行",
                "id": receive_data.data.fromUser.id},
            time=robot.time)
        receive_data.socketType = "sendData"
        res_data = get_data(receive_data)
        await manager.send_personal_json(res_data, robot.client_id, route)


@websocket_api.websocket("/chat/{client_id}")
async def get_process_data(websocket: WebSocket, client_id: str):
    # tokeninfo: TokenInfo = await check_jwt_token(token)
    # if not tokeninfo.isAdmin :
    #     raise PermissionNotEnough
    route = 'chat'
    await manager.connect(client_id, route, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            socketType = data.get('socketType', "")
            receive_data = SendDataModel(**data)
            if socketType == 'heartBeat':
                receive_data.data = 'pong'
                await manager.send_personal_json(receive_data.model_dump(), client_id, route)
                continue
            elif socketType == 'userInfo':
                # receive_data.data: ChatItemModel
                robot = robotsManager.get_robot(client_id, receive_data.data.toContactId)
                print(client_id, receive_data.data.toContactId)
                if robot is None:
                    robotsManager.add_robot(client_id, receive_data.data.toContactId)
                    robot = robotsManager.get_robot(client_id, receive_data.data.toContactId)
                if robot is not None:
                    await responseUser(receive_data, robot, route)
    except WebSocketDisconnect as e:
        manager.disconnect(client_id, route)
        robotsManager.remove_all_robot(client_id)
        logger.error(f'websocket连接出错,因为：{e}')
