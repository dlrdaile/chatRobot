from fastapi import FastAPI, Request
from core.logger import logger
from utils import resp_500


# 权限验证 https://www.cnblogs.com/mazhiyong/p/13433214.html
# 得到真实ip https://stackoverflow.com/questions/60098005/fastapi-starlette-get-client-real-ip
# nginx 解决跨域请求 https://segmentfault.com/a/1190000019227927

def register_middleware(app: FastAPI):
    """ 请求拦截与响应拦截 -- https://fastapi.tiangolo.com/tutorial/middleware/ """

    @app.middleware("http")
    async def intercept(request: Request, call_next):
        logger.info(f"访问记录:IP:{request.client.host}-method:{request.method}-url:{request.url}")
        try:
            return await call_next(request)  # 返回请求(跳过token)
        except Exception as e:
            logger.error(f'服务其发送错误 -- {e}')
            return resp_500(msg=f'服务其发送错误 -- {e}')
