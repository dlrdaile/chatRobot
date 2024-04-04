from enum import Enum

from fastapi import APIRouter
from pydantic import BaseModel
from core.logger import logger
from robot.zhipuModel import ZhiPuChat
from utils.resp_code import resp_200, resp_400


# 定义可选模型的枚举
class LLMPlatform(str, Enum):
    ZhangXueYou = "ZhangXueYou"
    Ali = "Ali"


class ApiKeyModel(BaseModel):
    api_key: str
    llm_platform: LLMPlatform
    llm_model: str
    user_id: str


apiKey_api = APIRouter(prefix='/apiKey')


@apiKey_api.post("/validate")
async def validate(api_key_model: ApiKeyModel):
    logger.info(f"api_key_model: {api_key_model}")
    try:
        api_key = api_key_model.api_key
        chat_client = ZhiPuChat(api_key)
        res = await chat_client.chat("你好")
        return resp_200(data={'valid': True, 'api_key': api_key})
    except Exception as e:
        logger.error(f"api_key_model: {api_key_model}")
        return resp_400(data=str(e))
