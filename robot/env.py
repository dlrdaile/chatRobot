prompt = '''徐天行是一名陆军士兵，陷入了时间循环。他早上8:00在火车上醒来，火车上有一枚炸弹，会在8:20经过西九龙站后爆炸，也可能由策划者通过电话提前引爆，他逃出时间循环的唯一办法是找到爆炸的策划者并阻止炸弹的爆炸。如果炸弹引爆，无论他是否在火车上，都会立即重新开始循环。


======================================   火车上人员的信息   =================================

周梓萱：在火车上与徐天行相邻座位的女性，她是一个艺术家，对生活感到失望。徐天行会对她产生好感，如果在火车上探索会优先找她对话。

钱德明：火车上的一名香港男子，最初被徐天行误认为是爆炸的策划者。他在火车上的行为显得紧张和可疑，他从火车的卫生间匆忙出来后，表现得非常焦虑。他穿着花衬衫，花臂纹身，看着像黑帮。当火车靠近西九龙站时，钱德明急匆匆地离开座位，试图尽快下车。但当火车爆炸发生时，钱德明的手机并没有响起，这意味着他并不是通过手机引爆炸弹的人。

孙立诚：30岁不易被注意的商务人士，火车爆炸的策划者。他在火车上故意丢失了自己的钱包，试图在爆炸发生后使自己看起来像是另一名受害者。当火车靠近西九龙站时，孙立诚表现出急切想要下车的行为。而在西九龙站，他再次试图丢弃自己的钱包。他的手机是炸弹的引爆装置，如果拨打电话就会引爆炸弹。

周子轩：普通的上班族，他的体型和穿着表明他可能过着舒适的生活，可能对工作感到压力，因此在火车上享受他的饮料，试图放松自己。他可能有一个温馨的家庭，每天通勤去城市工作，晚上回家与家人团聚。

孙浩然：一个充满活力的大学生，戴着耳机沉浸在自己的音乐世界中，他在去往学校的路上，耳机里播放的是他最喜欢的乐队的歌曲。

钟伯年：一位退休的长者，他的眼神和举止透露出岁月的沉淀和智慧。他正在享受退休生活，乘坐火车去看望老朋友。

韩煜晨： 一位热爱旅行的背包客，他的打扮和随身携带的背包表明他刚从一次冒险旅行中回来，他正回顾刚刚结束的旅行经历。


======================================  你的任务   =================================

在了解故事背景后，你需要充当这个世界的控制者，徐天行会做出一些行为，你需要根据背景设定来给出反馈。对于没有明确给出的信息，请你自行合理补充。例如，当徐天行想要随机与人交谈时，你应该在火车上找一个人，以他的身份与徐天行交谈。当徐天行在车厢中探索时，他可能在卫生间发现炸弹，也可能听到乘客的谈话等。每个行动都会花费时间，如果到了8:20徐天行仍然没有阻止炸弹爆炸，或他的行为导致孙立诚提前引爆炸弹，则立即结束循环。注意，当徐天行没有主动要搜索关于炸弹的线索时，不要提及炸弹。

请注意，尽量在多次循环后再让徐天行发现真相并成功阻止炸弹爆炸。

======================================  循环历史 ==================================

{}

======================================  当前循环 ==================================

{}

徐天行当前操作为：
{}

作为这个世界的控制者，对于这一次操作，请以以下格式输出回应，不要包含其它任何输出：
注意：对于当前循环第一次见的人物，用外貌指代。注意车上的人都是陌生人，徐天行并不能在交谈前知道对方的名字，交谈不一定能取得对方的信任。如果两个人发生了交谈，请模拟出交谈的具体内容。注意，当徐天行没有主动要搜索关于炸弹的线索时，不要提及炸弹。

回应：（徐天行操作的结果，以第三人称描述，只有知道名字的人物用名字指代，否则不要以任何形式返回名字，仅描述一件事即可）
时间：（请估计徐天行执行操作需要的分钟数，只包含一个正整数，不带符号和文字）
'''


from .zhipu import chat
import re

class Env():
    def __init__(self):
        self.loop_history = []
        self.loop = [["8:00", "徐天行从火车上醒来"]] # (time, response)

    def new_loop(self):
        self.loop_history.append(self.loop)
        self.loop = [["8:00", "徐天行从火车上醒来"]]

    def construct_prompt_loop(self, loop, i):
        return f"第{i+1}次循环：\n" + "\n".join([f"{time} {response}" for (time, response) in loop])

    def construct_prompt_loop_history(self):
        return "\n\n".join([self.construct_prompt_loop(loop, i) for i, loop in enumerate(self.loop_history)])

    def construct_prompt(self, action):
        return prompt.format(
            self.construct_prompt_loop_history(),
            self.construct_prompt_loop(self.loop, len(self.loop_history)),
            f"{action[0]} {action[1]}"
        )

    def act(self, action):
        prompt = self.construct_prompt(action)

        retry = 0
        while True:
            ret = chat(prompt)
            # print("====================")
            # print(prompt)
            # print("====================")
            print(ret)
            time = None
            response = None
            lines = ret.split('\n')
            for line in lines:
                if line.startswith('回应：'):
                    response = line[3:].strip()
                elif line.startswith('时间：'):
                    time = line[3:].strip()

            nums = [int(num) for num in re.findall(r'\d+', time)]
            if len(response) > 0 and len(nums) == 1:
                self.loop.append([action[0], response])
                return response, nums[0]

            retry += 1
            if retry >= 3:
                exit(0)



# ======================================   确定真正的炸弹策划者的可能步骤   =================================

# ### 第一次循环：
# - 徐天行醒来。
# - 他开始探索火车，试图理解自己的环境和情况。
# - 火车爆炸，循环结束。

# ### 第二次循环：
# - 徐天行再次醒来，开始更快地适应环境。
# - 他与周梓萱交谈，试图了解火车上的乘客。他询问他们是否注意到了任何不寻常的事情，或者是否有人行为怪异。
# - 他注意到一些异常情况，比如钱德明的可疑行为，这让他成为了初步的嫌疑人。
# - 火车爆炸，循环结束。

# ### 第三次循环：
# - 徐天行开始更加积极地寻找线索。
# - 他在火车的卫生间发现了炸弹，并意识到真正的策划者可能在火车上。
# - 他试图阻止爆炸，但未能成功。
# - 火车爆炸，循环结束。

# ### 第四次循环：
# - 徐天行决定直接面对钱德明，怀疑他是凶手。
# - 他在西九龙站与钱德明对峙，但发现钱德明并非真凶。钱德明的紧张只是因为他感到不适，而且他在火车爆炸时并没有使用手机。
# - 火车爆炸，循环结束。

# ### 第五次循环：
# - 徐天行注意到了孙立诚的异常行为。孙立诚在火车即将到达西九龙站时匆忙下车，并且在之前的行为中表现出了明显的逃避意图。徐天行意识到孙立诚可能是真正的凶手。
# - 他在火车上与孙立诚对峙，并设法获取了他的手机。
# - 火车爆炸，循环结束。

# ### 第六次循环：
# - 徐天行在火车上与周梓萱有了更深入的交流。
# - 他试图说服周梓萱下车，以避免爆炸。
# - 火车爆炸，循环结束。

# ### 第七次循环：
# - 徐天行再次尝试说服周梓萱下车，但未能成功。
# - 他在火车上拨打110报警，试图改变事件的结果。
# - 火车爆炸，循环结束。

# ### 最终循环：
# - 通过与孙立诚的对峙，徐天行揭露了孙立诚的动机和计划。孙立诚试图通过否认和伪装来逃避责任，但徐天行通过威胁和审问最终迫使孙立诚暴露了自己的罪行。最终阻止了爆炸发生。