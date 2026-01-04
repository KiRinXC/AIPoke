import random
import logging

from AIPoke.utili.data_manager import CFG_USER

class Random:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.cfg = CFG_USER
        self.prob = self.cfg['prob']  # 挂机概率
        self.AFK = self.cfg['AFK']    # 挂机时间

    def gauss(self,start,end,peak=None):
        """返回一个 [low,high] 内三角形分布的随机时间"""
        if peak is None:
            peak = (start + end) / 2  # 默认峰值居中
        return random.triangular(start, end, peak)

    def uniform(self, low, high):
        """生成符合均匀分布的时间"""
        val = random.uniform(low, high)
        return val

    def hangup(self, start, end,peak=None):
        """生成下一步或者挂机时间"""
        if random.random() < self.prob:  # 选 slow
            slow_time = self.gauss(self.AFK[0], self.AFK[2],self.AFK[1])
            self.logger.warning(f"等待挂机倒计时：{slow_time:.2f}")
            return slow_time
        else:  # 选 fast,
            if peak is None:
                peak = (start + end) / 2  # 默认峰值居中
            return self.gauss(start,end,peak)

    def gen_loc(self, rio):
        x, y, width, height = rio[0], rio[1], rio[2], rio[3]
        loc_x = self.gauss(x, x+width)
        loc_y = self.gauss(y, y+height)
        return int(loc_x), int(loc_y)

