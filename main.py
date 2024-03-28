import uvicorn
from fastapi import FastAPI, Body, BackgroundTasks

from core.config import settings
from core.logger import logger
from contextlib import asynccontextmanager
from apis.websocket.process import manager
from robot import ml_models
# from db import init_db,init_data
from schema.websocket.SendDataModel import SendDataModel
from register import (
    register_mount,
    register_exception,
    register_cors,
    register_middleware,
    register_router,
    register_timer,
)


# from sqlmodel.sql.expression import Select,SelectOfScalar
# SelectOfScalar.inherit_cache = True  # type: ignore
# Select.inherit_cache = True  # type: ignore


def create_app(app):
    """ 注册中心 """
    register_cors(app)  # 注册跨域请求

    register_middleware(app)  # 注册请求响应拦截

    register_mount(app)  # 挂载静态文件

    register_exception(app)  # 注册捕获全局异常

    register_router(app)  # 注册路由


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("日志初始化成功！！！")  # 初始化日志
    register_timer(app)  # 注册定时器
    # ml_models["actor"] = Actor()
    # ml_models["env"] = Env()
    yield
    ml_models.clear()
    logger.info("系统程序被关闭了")


app = FastAPI(lifespan=lifespan)
create_app(app)  # 加载注册中心


async def background_task():
    print(123)


@app.get("/")
async def read_root(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_task)
    return {"Hello": "World"}


@app.post("/")
async def write_root(sendData: SendDataModel):
    route = 'chat'
    id = '123'
    if manager.manager_exit(route, id):
        await manager.send_personal_json(sendData.dict(), id, route)
        return {"result": "success"}
    return {"result": "fail"}


if __name__ == '__main__':
    # uvicorn.run(app='main:app', host="127.0.0.1", port=8000)
    uvicorn.run(app='main:app', host=settings.DEFAULT_HOST, port=settings.DEFAULT_PORT, reload=True)
