#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# @Time : 2022/1/8 23:06
# @Author : zxiaosi
# @desc : 注册路由
from fastapi import FastAPI
from apis import *
from core.config import settings


# from apis import app_router
# from apis.deps import get_current_user
# from apis.common import redis_check, login, dashboard


def register_router(app: FastAPI):
    """ 注册路由 """
    # app.include_router(test_api,prefix="/apis/test")
    # # app.include_router(redis_check.router, prefix=settings.API_PREFIX, tags=["Redis"])  # Redis(不需要权限)
    # #
    app.include_router(apiKey_api, prefix=settings.API_PREFIX, tags=["apiKey"])  # Login(权限在每个接口上)
    # app.include_router(commons_api, prefix=settings.API_PREFIX, tags=["Common"])  # Login(权限在每个接口上)
    # app.include_router(client_api,prefix=settings.API_PREFIX,tags=['Client'])
    # app.include_router(admin_api,prefix=settings.API_PREFIX,tags=['Admin'])
    app.include_router(websocket_api, tags=['Websocket'])
    #
    # app.include_router(dashboard.router, prefix=settings.API_PREFIX, tags=["Dashboard"],
    #                    dependencies=[Security(get_current_user, scopes=[])])  # Dashboard(不需要权限,但需要登录)
    #
    # # 权限(权限在每个接口上)
    # app.include_router(app_router, prefix=settings.API_PREFIX)
