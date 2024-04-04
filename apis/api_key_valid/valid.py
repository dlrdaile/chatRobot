from fastapi import APIRouter

from core.logger import logger
from robot.robot import RobotManager
from robot.zhipuModel import Chat
from schema.websocket.ChatItemModel import ApiKeyModel
from utils.resp_code import resp_200, resp_400

# 定义可选模型的枚举


apiKey_api = APIRouter(prefix='/apiKey')


@apiKey_api.post("/validate")
async def validate(requestModel: ApiKeyModel):
    logger.info(f"api_key_model: {requestModel}")
    try:
        res = await RobotManager.create_chat_client(requestModel)
        return resp_200(data=requestModel.dict())
    except Exception as e:
        logger.error(f"api_key_model: {requestModel}")
        return resp_400(data=str(e))
