import time
import pydirectinput
import random

from AIPoke.utili.data_manager import CFG_KEY
from AIPoke.actor.Random import Random
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False
class Key:
    def __init__(self):
        self.cfg = CFG_KEY
        self.rand = Random()
        self.min = self.cfg['min']  # 按键最短时间
        self.max = self.cfg['max']  # 按键最长时间
        self.shuffle_prob = self.cfg['shuffle_prob']   # 打乱按键顺序的概率

        self.right = self.cfg['right']
        self.left = self.cfg['left']
        self.up = self.cfg['up']
        self.down = self.cfg['down']
        self.A = self.cfg['A']
        self.B = self.cfg['B']


    def press(self, key):
        """
        模拟：按下 -> 随机持续 -> 松开
        """
        time.sleep(self.rand.hangup(0.0,0.5,0.04))
        pydirectinput.keyDown(key)
        time.sleep(self.rand.gauss(0.03,0.1))
        pydirectinput.keyUp(key)

    def press_with_shuffle(self, order):
        """随机打乱按键"""
        if random.random() < self.shuffle_prob:
            order[0], order[1] = order[1], order[0]  # 交换
        for k in order:
            self.press(k)


class KOptions(Key):
    """对战界面的四个选项"""
    def __init__(self):
        super().__init__()
        self.escape = [self.right,self.down]
        
    def escape_press(self):
        self.press_with_shuffle(self.escape)
        self.press(self.B)

class KBar(Key):
    def __init__(self):
        super().__init__()
        self.perfume = self.cfg['perfume']
        self.spray = self.cfg['spray']
        self.sweet_scent = self.cfg['sweet_scent']
        self.fish_rod = self.cfg['fish_rod']

    def perfume_press(self):
        self.press(self.perfume)

    def spray_press(self):
        self.press(self.spray)

    def sweet_scent_press(self):
        self.press(self.sweet_scent)

    def fish_rod_press(self):
        self.press(self.fish_rod)



