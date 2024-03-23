from zhipuai import ZhipuAI

client = ZhipuAI(api_key="bb068c827c8a42bb37fbdbb81ae82ff2.mmxjKl4ScNmdVVAV")


def chat(prompt, sys_prompt="", history=None):
    messages = []
    if sys_prompt != "":
        messages.append({"role": "system", "content": sys_prompt})
    if history is not None:
        messages += history
    if prompt != "":
        messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="glm-4",
        messages=messages
    )
    return response.choices[0].message.content
