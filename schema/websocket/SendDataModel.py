from pydantic import BaseModel
from typing import Union
from .ChatItemModel import ChatItemModel


class SendDataModel(BaseModel):
    """
    发送数据模型
    """
    data: str | ChatItemModel
    socketType: str
