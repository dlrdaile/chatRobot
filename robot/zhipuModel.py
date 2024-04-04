from zhipuai import ZhipuAI
import time
import jwt
import aiohttp




class ZhiPuChat:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    async def chat(self, prompt: str, sys_prompt="", history=None):
        messages = []
        if sys_prompt != "":
            messages.append({"role": "system", "content": sys_prompt})
        if history is not None:
            messages += history
        if prompt != "":
            messages.append({"role": "user", "content": prompt})
        async with aiohttp.ClientSession() as session:
            data = {
                'model': 'glm-4',
                'messages': messages
            }
            headers = {
                'Authorization': f'Bearer {self.generate_token(self.api_key, 3600)}'
            }
            async with session.post(self.url, headers=headers, json=data) as response:
                result = await response.json()
                return result['choices'][0]['message']['content']
        # client = ZhipuAI(api_key=self.api_key)
        # response = client.chat.completions.create(
        #     model="glm-4",
        #     messages=messages
        # )
        # return response.choices[0].message.content

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


if __name__ == '__main__':
    import asyncio
    chat = ZhiPuChat("e32a4b442f4c64e8c792c16d3cdec1b0.s4njtj6LqPI4vHkL")
    print(asyncio.run(chat.chat("你好")))