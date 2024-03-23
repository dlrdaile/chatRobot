prompt = '''你是徐天行，是一名军人，Goodwin是你的朋友和上级。你在早上8:00醒来，发现自己处于一列火车上，不记得自己是如何到达这里的。你想知道发生了什么。你的相邻座位是一个女性，同车厢里还有一个充满活力的大学生，一个穿着花衬衫的男子，一个普通上班族，一位长者，一个背包客，一个中年商务男。

以下是你和Goodwin的聊天记录：
{}

以下是你的行动经历：
{}

现在时间是{}.

'''

prompts = {
    'action': '''
你现在可以依据Goodwin的最新指示进行行动，请以以下格式输出一行行动内容，不要有其它任何输出，不出现“我”，“你”等人称代词：
内容：xxx
''',
    'message': '''
你现在可以要将你在行动中看到的，没有汇报给Goodwin的内容，尽可能详细地描述给Goodwin。请以以下格式输出一行消息内容，尽量轻快口语化：
内容：xxx
'''
}

try:
    from .zhipu import chat
except:
    from zhipu import chat

class Actor():
    def __init__(self):
        self.reset()

    def reset(self):
        self.actions = [] # (time, action, response)
        self.messages = [] # (time, speaker, message)
        self.time = "8:00"

    def construct_prompt(self, action):
        actions_str = "\n".join([f"{time} {action} {responce}" for (time, action, responce) in self.actions])
        if actions_str == '':
            actions_str = "无行动"

        messages_str = "\n".join([f"{time} {speaker}: {message}" for (time, speaker, message) in self.messages])
        if messages_str == '':
            messages_str = "无记录"

        return prompt.format(messages_str, actions_str, self.time) + prompts[action]

    def add_message(self, message):
        print(message)
        self.messages.append(message)

    def user_input(self, message):
        self.add_message([self.time, 'Goodwin', message])

    def add_action(self, action):
        self.actions.append(action)

    def act(self, time, action):
        self.time = time
        prompt = self.construct_prompt(action)

        retry = 0
        while True:
            ret = chat(prompt)
            # print("====================")
            # print(prompt)
            # print("====================")
            print(ret)

            message = None
            lines = ret.split('\n')
            for line in lines:
                if line.startswith('内容：'):
                    message = line[3:].strip()

            if message is None or len(message) < 2: continue

            if action == 'message':
                self.add_message([self.time, '徐天行', message])
                return message
            elif action == 'action':
                action = [self.time, message, None]
                return action

            retry += 1
            if retry >= 3:
                exit(0)