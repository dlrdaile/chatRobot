from pydantic import BaseModel

from .ChatItemModel import ChatItemModel, ApiKeyModel


class SendDataModel(BaseModel):
    """
    发送数据模型
    """
    data: str | ChatItemModel | ApiKeyModel
    socketType: str
