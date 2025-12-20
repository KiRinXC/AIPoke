import time
import random
import pydirectinput
import numpy as np
import threading
import logging
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False

# 基础设置
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class Walker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.right = 'd'
        self.left = 'a'
        self.up = 'w'
        self.down = 's'

        self.opposites = {
            self.left: self.right,
            self.right: self.left,
            self.up: self.down,
            self.down: self.up
        }

        # 记录位置偏差 (秒)
        self.position_bias = 0.0

        self.MIN_WALK_TIME = 0.15

    def _move_one_way(self, key, mu, sigma, stop_event):
        """
        单向移动：带偏差修正 + 遇怪重置
        """
        try:
            # 1. --- 偏差修正逻辑 ---
            adjusted_mu = mu

            # 判断当前移动方向的正负 (右/下为正，左/上为负)
            direction_sign = 0
            if key in [self.right, self.down]:
                direction_sign = 1
                # 如果之前偏左了(bias < 0)，往右就要跑久一点来回正
                if self.position_bias < 0:
                    adjusted_mu = mu + abs(self.position_bias) * 0.5
            elif key in [self.left, self.up]:
                direction_sign = -1
                # 如果之前偏右了(bias > 0)，往左就要跑久一点来回正
                if self.position_bias > 0:
                    adjusted_mu = mu + self.position_bias * 0.5

            # 2. --- 生成随机时间 ---
            raw_duration = random.gauss(adjusted_mu, sigma)

            # 【物理防抖】: 最小值取 mu/2 和 0.15s 中的较大者
            # 0.15s 是为了防止时间太短角色只转身不走动
            duration = np.clip(raw_duration, self.MIN_WALK_TIME, mu * 2.0)

            # 3. --- 执行移动 ---
            pydirectinput.keyDown(key)
            start_time = time.time()
            interrupted = False

            while time.time() - start_time < duration:
                if stop_event.is_set():
                    interrupted = True
                    break
                time.sleep(0.005)

            actual_move_time = time.time() - start_time

            # 4. --- 结算偏差 ---
            if interrupted:
                # 只要遇怪(被打断)，说明位置安全，清空偏差
                # 将当前位置作为新的 "0点"
                self.position_bias = 0.0
                # print(">>> 遇怪！偏差清零，确立新原点")
            else:
                # 没遇怪：累积偏差，继续尝试回正
                self.position_bias += (direction_sign * actual_move_time)

            return interrupted

        finally:
            pydirectinput.keyUp(key)

    def patrol(self, start_dir, stop_event, mu, sigma):
        """
        通用巡逻入口
        """
        if start_dir not in self.opposites:
            return

        k1 = start_dir
        k2 = self.opposites[start_dir]

        # 每次重新开始巡逻时，也可以选择是否重置偏差
        # self.position_bias = 0.0

        try:
            while not stop_event.is_set():
                if self._move_one_way(k1, mu, sigma, stop_event): break
                if self._move_one_way(k2, mu, sigma, stop_event): break
        except Exception:
            pydirectinput.keyUp(k1)
            pydirectinput.keyUp(k2)



# ================== 测试代码 ==================
if __name__ == "__main__":
    walker = Walker()
    stop_signal = threading.Event()

    # 在子线程中启动移动
    t = threading.Thread(target=walker.patrol, args=(walker.right,stop_signal,1,0.1))

    print("2秒后开始移动...")
    pydirectinput.click(10, 10)
    pydirectinput.keyDown('d')
    pydirectinput.keyUp('d')
    time.sleep(2)

    # t.start()
    print("正在移动... (模拟 5秒后 遇怪停止)")

    pydirectinput.keyDown('a')
    # time.sleep(0.08)# +两格
    time.sleep(0.08+0.082*48)
    pydirectinput.keyUp('a')
    # time.sleep(30)
    print(">>> 触发停止信号！")
    # stop_signal.set()

    # t.join()
    print("已停止。")