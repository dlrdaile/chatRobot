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
from utils.time_utils import time_string_to_timestamp
from uuid import uuid4

websocket_api = APIRouter(prefix='/ws')
manager = ConnectionManager()


def get_data(data: SendDataModel) -> dict:
    # res_data = ResponseModel(data=data.model_dump())
    res_data = data
    # sql = select(Items)
    # result = {}
    # for item in result:
    #     pass
    return res_data.model_dump()


async def responseUser(receive_data: SendDataModel, id: int, route: str, t: int, time: int):
    actor = ml_models['actor']
    env = ml_models['env']
    # while True:
    #     print(actor.time)
    time_s = '8:{:02d}'.format(time)
    if t == 0:
        receive_content = receive_data.data.content
        message = actor.act(time_s, 'message')
        if isinstance(message, str):
            receive_data.data = ChatItemModel(
                content=message,
                sendTime=time_s,
                id=uuid4().hex,
                status="success",
                type="text",
                toContactId="123",
                fromUser={"avatar": "https://avatars.githubusercontent.com/u/52351022?v=4",
                          "displayName": "徐天行",
                          "id": "123"},
                time=time)
            receive_data.socketType = "sendData"
            res_data = get_data(receive_data)
            await manager.send_personal_json(res_data, id, route)
        actor.user_input(receive_content)
        time += 1
    else:
        action = actor.act(time_s, 'action')
        response, act_time = env.act(action)
        action[2] = response.replace('徐天行', '你')
        actor.add_action(action)
        time += act_time

    t = 1 - t
    if time >= 20:
        actor.reset()
        env.new_loop()
        time = 0
        t = 0
        print("=========================== Boom =============================")

    # message, action, currentTimeStr = actor.act()
    # if action is not None:
    #     response, time = env.act(action)
    #     action[2] = response.replace('徐天行', '你')
    #     actor.add_action(action)
    #     actor.time = time
    #     if message is not None:
    #         pass
    # elif message is not None:
    #     actor.user_input(receive_data.data.content)
    return t, time


@websocket_api.websocket("/chat")
async def get_process_data(websocket: WebSocket, background_tasks: BackgroundTasks):
    # tokeninfo: TokenInfo = await check_jwt_token(token)
    # if not tokeninfo.isAdmin :
    #     raise PermissionNotEnough
    route = 'chat'
    id = 123
    num = 0
    t = 0
    time = 0
    await manager.connect(id, route, websocket)

    # session = get_session()

    try:
        while True:
            data = await websocket.receive_json()
            socketType = data.get('socketType', "")
            receive_data = SendDataModel(**data)
            if socketType == 'heartBeat':
                receive_data.data = 'pong'
                await manager.send_personal_json(receive_data.model_dump(), id, route)
                continue
            elif socketType == 'userInfo':
                print(receive_data)
                # background_tasks.add_task(responseUser, receive_data, id, route)
                t, time = await responseUser(receive_data, id, route, t, time)
    except WebSocketDisconnect as e:
        manager.disconnect(id, route)
        logger.error(f'websocket连接出错,因为：{e}')
