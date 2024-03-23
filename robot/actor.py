prompt = '''你是徐天行，是一名军人，顾文博是你的朋友和上级，她是一名女性。你在早上8:00醒来，发现自己处于一列火车上，不记得自己是如何到达这里的。你想知道发生了什么。你的相邻座位是一个女性，同车厢里还有一个充满活力的大学生，一个穿着花衬衫的男子，一个普通上班族，一位长者，一个背包客，一个中年商务男。

以下是你的行动经历：
{}


现在时间是{}. 你可以选择两个操作之一：
A. 给顾文博发消息。要求：你说的话要符合你的行动经历，尽可能详细地描述你在行动中获得的见闻，尽量轻快口语化。不要留下任何待填补的内容。
B. 依据顾文博的最新指示进行行动。要求：输出行动内容，不出现“我”，“你”等人称代词。

如果顾文博建议或要求你进行某个行动，你必须选择行动。而如果你刚刚行动结束，你必须选择A，将行动的结果汇报给顾文博。仅有顾文博与你聊天或进一步了解信息时你可以给他连续发消息。注意，你必须只能选择其中一个，不要做假设性的输出。

请以以下格式输出回应，只包括三行内容：

你的思考：先判断顾文博是否让你行动，如果有则必须行动，不能违抗。请给出你做出选择的理由，并且**复述该操作的要求**。
操作：(A或B)
内容：xxx

注意：不要有多余的超过三行的输出！
'''

try:
    from .zhipu import Chat
except:
    from zhipu import Chat

class Actor():
    def __init__(self, chatClient: Chat):
        self.chatClient = chatClient
        self.reset()

    def reset(self):
        self.actions = [] # (time, action, response)
        self.messages = [] # (time, speaker, message)
        self.records = []
        self.time = "8:00"

    def construct_prompt(self):
        messages_str = "\n".join(self.records)
        if messages_str == '':
            messages_str = "无"

        return prompt.format(messages_str, self.time)

    def add_message(self, message):
        print(message)
        self.messages.append(message)

        (time, speaker, message) = message
        self.records.append(
            str(time) + " " +
            ('你向顾文博发消息：' if speaker == '徐天行' else '顾文博向你发消息：') + 
            message
        )

    def user_input(self, message):
        self.add_message([self.time, '顾文博', message])

    def add_action(self, action):
        self.actions.append(action)

        (time, action, response) = action
        self.records.append(f"{time} {action} {response}")

    def act(self, time):
        self.time = time
        prompt = self.construct_prompt()

        retry = 0
        while True:
            retry += 1
            if retry >= 5:
                exit(0)

            ret = self.chatClient.chat(prompt)
            message = None
            t = None
            lines = ret.split('\n')
            for line in lines:
                if line.startswith('内容：'):
                    message = line[3:].strip()
                elif line.startswith('操作：'):
                    t = line[3:].strip()

            if sum([line.startswith('操作：') for line in lines]) >= 2: continue
            if t is None or t not in ['A', 'B'] or message is None or len(message) < 2: continue

            # print("====================")
            # print(prompt)
            # print("====================")
            # print(ret)

            if t == 'A':
                self.add_message([self.time, '徐天行', message])
                return t, message
            elif t == 'B':
                action = [self.time, message, None]
                return t, action

