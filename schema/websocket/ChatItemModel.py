from pydantic import BaseModel


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
    fromUser: FromUserModel
    id: str
    sendTime: int | str
    status: str = "success"
    type: str
    toContactId: str
    time: int = 0


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
