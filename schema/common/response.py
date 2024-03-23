from pydantic import BaseModel


class ResponseModel(BaseModel):
    """
    响应模型
    """
    code: int = 200
    message: str = "success"
    data: dict = {}
    error: dict = {}

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            bytes: lambda v: v.decode(),
        }
