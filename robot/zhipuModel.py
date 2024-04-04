import time
from enum import Enum
from core.logger import logger

import jwt
from langchain_openai import ChatOpenAI
from langchain_community.llms.tongyi import Tongyi
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, \
    ChatPromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import BaseOutputParser


class LLMPlatform(str, Enum):
    ZhiPu = "ZhiPu"
    TongYi = "TongYi"


class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")


class ChatModel:
    def __init__(self):
        self.model_set = []
        self.llm = None

    def _generate_chat_prompt(self, sys_prompt=None, history=None):
        message = []
        if sys_prompt is not None and sys_prompt != "":
            message.append(SystemMessagePromptTemplate.from_template(sys_prompt))
        if history is None:
            history = []
        for h in history:
            message.append(AIMessagePromptTemplate.from_template(h))
        human_template = "{input}"
        message.append(HumanMessagePromptTemplate.from_template(human_template))
        chat_prompt = ChatPromptTemplate.from_messages(message)
        return chat_prompt

    async def chat(self, prompt, sys_prompt=None, history=None, **kwargs):
        if self.llm is None:
            raise NotImplementedError
        chat_prompt = self._generate_chat_prompt(sys_prompt, history)
        chain = LLMChain(
            llm=self.llm,
            prompt=chat_prompt,
            # output_parser=CommaSeparatedListOutputParser()
        )
        result = await chain.ainvoke({"input": prompt})
        # logger.info(f"chat result: {result}")
        return result["text"]


class ZhipuChatModel(ChatModel):
    def __init__(self, api_key: str, model: str = "glm-4"):
        super().__init__()
        self.api_key = api_key
        self.model_set = ['glm-4', ]
        if model not in self.model_set:
            raise ValueError(f"invalid model, model must be one of {self.model_set}")
        self.model = model
        # self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_base="https://open.bigmodel.cn/api/paas/v4",
            openai_api_key=self.generate_token(self.api_key, 3600)
        )

    async def chat(self, prompt, sys_prompt=None, history=None, **kwargs):
        self.llm.openai_api_key = self.generate_token(self.api_key, 3600)
        return await super().chat(prompt, sys_prompt, history, **kwargs)

    def generate_token(self, apikey: str, exp_seconds: int):
        try:
            id, secret = apikey.split(".")
        except Exception as e:
            raise Exception("invalid apikey", e)

        payload = {
            "api_key": id,
            "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
            "timestamp": int(round(time.time() * 1000)),
        }

        return jwt.encode(
            payload,
            secret,
            algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )


class TongyiChatModel(ChatModel):
    def __init__(self, api_key: str, model: str = "qwen-max"):
        super().__init__()
        self.api_key = api_key
        self.model_set = ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-max-longcontext']
        if model not in self.model_set:
            raise ValueError(f"invalid model, model must be one of {self.model_set}")
        self.model = model
        self.llm = Tongyi(dashscope_api_key=self.api_key, model_name=self.model)


class Chat:
    def __init__(self, api_key: str, platform: LLMPlatform = LLMPlatform.TongYi, model: str = "qwen-max"):
        self.chat_model = None
        if platform == LLMPlatform.TongYi:
            self.chat_model = TongyiChatModel(api_key, model)
        elif platform == LLMPlatform.ZhiPu:
            self.chat_model = ZhipuChatModel(api_key, model)

    async def chat(self, prompt: str, sys_prompt=None, history=None, **kwargs):
        ret = await self.chat_model.chat(prompt, sys_prompt, history, **kwargs)
        return ret


if __name__ == '__main__':
    import asyncio

    # chat = Chat(api_key="sk-2881a944a074494c8de43fdedd65d162", model="qwen-max", platform="tongyi")
    chat = Chat(api_key="e32a4b442f4c64e8c792c16d3cdec1b0.s4njtj6LqPI4vHkL", model="glm-4", platform=LLMPlatform.ZhiPu)
    # chat = ZhipuChatModel(api_key="e32a4b442f4c64e8c792c16d3cdec1b0.s4njtj6LqPI4vHkL", model="glm-4")
    print(asyncio.run(chat.chat("你叫什么名字")))
