import logging
import random

from AIPoke.actor.Key import KOptions,KBar
from AIPoke.actor.Mouse import MOptions,MBar
from AIPoke.utili.data_manager import CFG_USER

class Actor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cfg = CFG_USER
        self.options_prob = self.cfg['options_prob']
        self.bar_prob = self.cfg['bar_prob']

    def select(self, key, mouse, item, prob):
        """对应使用键盘的概率"""
        if random.random() < prob:
            self.logger.info(f"键盘-->{item}")
            return key
        else:
            self.logger.info(f"鼠标-->{item}")
            return mouse


class AOptions(Actor):
    def __init__(self):
        super().__init__()
        self.K = KOptions()
        self.M = MOptions()

    def escape(self):
        self.select(self.K.escape_press, self.M.escape_click,"逃跑" ,self.options_prob)()



class ABar(Actor):
    def __init__(self):
        super().__init__()
        self.K = KBar()
        self.M = MBar()

    def perfume(self):
        self.select(self.K.perfume_press, self.M.perfume_click,"香水" ,self.bar_prob)()

    def spray(self):
        self.select(self.K.spray_press, self.M.spray_click,"喷雾" ,self.bar_prob)()

    def sweet_scent(self):
        self.select(self.K.sweet_scent_press, self.M.sweet_scent_click,"甜甜香气" ,self.bar_prob)()


    def fish_rod(self):
        self.select(self.K.fish_rod_press, self.M.fish_rod_click,"钓鱼竿" ,self.bar_prob)()