from zhipuai import ZhipuAI

"bb068c827c8a42bb37fbdbb81ae82ff2.mmxjKl4ScNmdVVAV"


class Chat:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def chat(self, prompt: str, sys_prompt="", history=None):
        messages = []
        if sys_prompt != "":
            messages.append({"role": "system", "content": sys_prompt})
        if history is not None:
            messages += history
        if prompt != "":
            messages.append({"role": "user", "content": prompt})
        client = ZhipuAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="glm-4",
            messages=messages
        )
        return response.choices[0].message.content
