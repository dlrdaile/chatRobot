from core.logger import logger
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from apis.websocket.process import manager, robotsManager


def detectRobotActivateJob():
    logger.info("定时器开始清理无用机器人！！！")
    robotsManager.cleanNoUseRobot()


def register_timer(app: FastAPI):
    sche = BackgroundScheduler()
    sche.add_job(detectRobotActivateJob, next_run_time=datetime.now(), trigger='interval', minutes=5,
                 id="detectRobotActivateJob")

    app.state.sche = sche
    logger.info("定时器注册成功！！！")
    sche.start()
