#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# @Time : 2022/1/9 16:48
# @Author : zxiaosi
# @desc : 跨域请求
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings


def register_cors(app: FastAPI):
    """ 跨域请求 -- https://fastapi.tiangolo.com/zh/tutorial/cors/ """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=("*",),
        allow_headers=("*",),
    )
