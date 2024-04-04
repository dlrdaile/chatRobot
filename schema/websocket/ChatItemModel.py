from pydantic import BaseModel
from typing import Optional

from robot.zhipuModel import LLMPlatform


class FromUserModel(BaseModel):
    """
    发送者模型
    """
    avatar: str
    displayName: str
    id: str


class ChatItemModel(BaseModel):
    """
    聊天项模型
    """
    content: str
    fromUser: Optional[FromUserModel] = None
    id: str
    sendTime: int | str
    status: str = "success"
    type: str = "text"
    toContactId: str
    time: int = 0
    end: int = 0
class ApiKeyModel(BaseModel):
    api_key: str
    llm_platform: LLMPlatform
    llm_model: str
    client_id: str

if __name__ == '__main__':
    from uuid import uuid4

    data = ChatItemModel(
        content="123",
        sendTime=12321,
        id=uuid4().hex,
        status="success",
        type="text",
        toContactId="123",
        fromUser={"avatar": "https://avatars.githubusercontent.com/u/52351022?v=4",
                  "displayName": "徐天行",
                  "id": "123"})
