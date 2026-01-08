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

        self.opposites = {
            self.left: self.right,
            self.right: self.left,
            self.up: self.down,
            self.down: self.up
        }

        # 记录位置偏差 (秒)
        self.position_bias = 0.0

        self.MIN_WALK_TIME = 0.15

    def patrol_x(self,move_event,obs_event,rio):
        self.patrol(move_event,obs_event,[self.right,self.left],rio)

    def patrol_y(self,move_event,obs_event,rio):
        self.patrol(move_event,obs_event,[self.up,self.down],rio)

    def patrol(self, move_event, obs_event, direction,rio):
        """
        :param move_event: 移动事件
        :param obs_event: 撞墙事件
        :param direction: 移动方向
        :param rio: 随机时间范围
        """

        # 初始方向随机
        current_dir = random.choice(direction)

        # 标记上一次是否是因为"遇怪/停止"而中断的
        # 如果是，下一次移动方向随机；如果不是，下一次反向
        is_interrupted = False

        while move_event.is_set():

            # 决定本次移动的方向
            if is_interrupted:
                # 如果上次是被打断的（比如刚打完怪），随机选一个方向开始
                current_dir = random.choice(direction)
            else:
                # 正常情况：往反方向走
                current_dir = self.opposites.get(current_dir)

            # 决定本次移动的时间 (均匀分布)
            duration = random.uniform(rio[0], rio[1])

            # 开始移动
            pydirectinput.keyDown(current_dir)
            start_time = time.time()

            try:
                # 循环检查 (直到时间结束)
                while time.time() - start_time < duration:

                    # check 1: 是否不允许移动了? (遇怪/脚本暂停)
                    if not move_event.is_set():
                        is_interrupted = True
                        self.logger.info("停止移动")
                        break  # 立即跳出
                    time.sleep(0.15)
                    # check 2: 是否撞墙?
                    if obs_event.is_set():
                        is_interrupted = False
                        self.logger.warning(f"方向[{current_dir}]->撞墙")
                        break  # 立即跳出，换方向

                    # 极短睡眠，防止死循环占用100% CPU，同时保证响应速度


            finally:
                # 无论如何，第一时间松开按键
                pydirectinput.keyUp(current_dir)


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