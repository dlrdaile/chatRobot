"""
author:dlr123
date:2022年06月14日
"""
import time
from collections import defaultdict
from typing import Union, Dict

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

from core.logger import logger
import enum


class WebSocketState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, id: str, route: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[route][id] = websocket

    def disconnect(self, id: str, route: str):
        self.active_connections[route].pop(id)

    def get_websocket(self, id: str, route: str):
        return self.active_connections[route].get(id, None)

    async def send_personal_text(self, message: str, id: str, route: str):
        websocket = self.get_websocket(id, route)
        if websocket is not None and websocket.client_state.value == 1:
            await websocket.send_text(message)
        else:
            raise Exception(f"websocket {id} not connected")

    async def send_personal_json(self, message: Union[dict, list], id: str, route: str):
        message = jsonable_encoder(message)
        websocket = self.get_websocket(id, route)
        if websocket is not None and websocket.client_state.value == 1:
            await websocket.send_json(message)
        else:
            raise Exception(f"websocket {id} not connected")

    async def send_personal_stream(self, message, id: str, route: str):
        websocket = self.get_websocket(id, route)
        if websocket is not None and websocket.client_state.value == 1:
            await websocket.send_bytes(message)
        else:
            raise Exception(f"websocket {id} not connected")

    async def broadcast_text(self, route: str, message: str):
        for key, connection in self.active_connections[route].items():
            await self.send_personal_text(message, key, route)

    async def broadcast_json(self, route: str, message: Union[dict, list]):
        message = jsonable_encoder(message)
        for key, connection in self.active_connections[route].items():
            await self.send_personal_json(message, key, route)

    async def broadcast_stream(self, route: str, message):
        for key, connection in self.active_connections[route].items():
            await self.send_personal_stream(message, key, route)

    def manager_exit(self, route: str, id: str):
        return self.active_connections.get(route, {}).get(id, None) is not None
