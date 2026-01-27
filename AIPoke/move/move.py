import time
import random
import pydirectinput
import numpy as np
import threading
import logging
from AIPoke.utili.data_manager import CFG_KEY
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class Walker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.key = CFG_KEY
        self.right = self.key["right"]
        self.left = self.key["left"]
        self.up = self.key["up"]
        self.down = self.key["down"]

        self.map ={
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
        }
        self.opposites = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
        }

        # 记录位置偏差 (秒)
        self.position_bias = 0.0

        self.MIN_WALK_TIME = 0.15

    def patrol_x(self,move_event,obs_event,rio):
        self.patrol(move_event,obs_event,["right","left"],rio)

    def patrol_y(self,move_event,obs_event,rio):
        self.patrol(move_event,obs_event,["up","down"],rio)

    def mm(self):
        pydirectinput.keyDown(self.left)
        time.sleep(0.2)
        pydirectinput.keyUp(self.left)

    def patrol(self, move_event, obs_event: dict, direction, rio):
        """
        :param move_event:      全局“是否允许继续移动”事件
        :param obs_event:       各方向撞墙事件  dict[str, threading.Event]
        :param direction:       允许的移动方向列表
        :param rio:             每次移动时间范围 (min, max)
        """
        current_dir = random.choice(direction)  # 初始方向
        is_interrupted = False  # 上次是否因“遇怪”中断

        while move_event.is_set():
            # 1. 选方向
            if is_interrupted:
                current_dir = random.choice(direction)
            else:
                current_dir = self.opposites.get(current_dir)

            # 2. 选时长
            duration = random.uniform(rio[0], rio[1])
            self.logger.info(f"向[{current_dir}]移动{duration:.2f}秒")
            pydirectinput.keyDown(self.map[current_dir])
            start_time = time.time()

            try:
                while time.time() - start_time < duration:
                    # 2.1 全局停止信号
                    if not move_event.is_set():
                        is_interrupted = True
                        self.logger.info("停止移动")
                        break

                    # 2.2 只检查当前方向是否撞墙
                    if obs_event.get(current_dir) and obs_event[current_dir].is_set():
                        is_interrupted = False
                        self.logger.warning(f"方向[{current_dir}]->撞墙")
                        # obs_event[current_dir].clear()  # 清除本次信号
                        break
                    time.sleep(0.05)  # 适当睡眠，降低 CPU
            finally:
                pydirectinput.keyUp(self.map[current_dir])

# time.sleep(2)
# waker = Walker()
# waker.mm()

#
# # ================== 测试代码 ==================
# if __name__ == "__main__":
#     walker = Walker()
#     stop_signal = threading.Event()
#
#     # 在子线程中启动移动
#     t = threading.Thread(target=walker.patrol, args=(walker.right,stop_signal,1,0.1))
#
#     print("2秒后开始移动...")
#     pydirectinput.click(10, 10)
#     pydirectinput.keyDown('d')
#     pydirectinput.keyUp('d')
#     time.sleep(2)
#
#     # t.start()
#     print("正在移动... (模拟 5秒后 遇怪停止)")
#
#     pydirectinput.keyDown('a')
#     # time.sleep(0.08)# +两格
#     time.sleep(0.08+0.082*48)
#     pydirectinput.keyUp('a')
#     # time.sleep(30)
#     print(">>> 触发停止信号！")
#     # stop_signal.set()
#
#     # t.join()
#     print("已停止。")


