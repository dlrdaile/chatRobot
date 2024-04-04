class AliChat:
    def __init__(self, api_key: str, model="qwen-plus"):
        self.model_set = ['qwen-turbo', 'qwen-plus', 'qwen-max', 'qwen-max-longcontext']
        if model not in self.model_set:
            raise Exception(f"invalid model, model must be one of {self.model_set}")
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
        # async with aiohttp.ClientSession() as session:
        #     data = {
        #         'model': 'glm-4',
        #         'messages': messages
        #     }
        #     headers = {
        #         'Authorization': f'Bearer {self.generate_token(self.api_key, 3600)}'
        #     }
        #     async with session.post(self.url, headers=headers, json=data) as response:
        #         result = await response.json()
        #         return result['choices'][0]['message']['content']
