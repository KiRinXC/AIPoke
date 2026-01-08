import time
import pydirectinput

from AIPoke.actor.Point import Point
from AIPoke.actor.Random import Random
from AIPoke.utili.data_manager import RIO_MOUSE
# ================= 全局配置 =================
pydirectinput.PAUSE = 0.0
pydirectinput.FAILSAFE = False

class Mouse:
    def __init__(self):
        self.rand = Random()
        self.rio = RIO_MOUSE
        self.min = self.rio["min"]  #
        self.max = self.rio["max"]
        self.shake_drift_prob = self.rio["shake_drift_prob"]
        self.random_drift_prob = self.rio["random_drift_prob"]
        self.point = Point()


    def click(self,rio,button='left'):
        x, y = self.rand.gen_loc(rio)
        self.point.move_to(x,y)
        # 鼠标按下
        pydirectinput.mouseDown(x=x, y=y, button=button, _pause=False)

        # 随机按下时长
        time.sleep(self.rand.gauss(self.min,self.max))

        # 鼠标抬起
        pydirectinput.mouseUp(button=button, _pause=False)
        # 鼠标发生偏移
        self.point.shake_drift(prob=self.shake_drift_prob)
        time.sleep(self.rand.gauss(0,4.0,0.5))
        self.point.random_drift(prob=self.random_drift_prob)

class MOptions(Mouse):
    def __init__(self):
        super().__init__()
        self.battle = self.rio["battle"]
        self.bag = self.rio["bag"]
        self.pokemon = self.rio["pokemon"]
        self.escape = self.rio["escape"]

    def battle_click(self):
        self.click(self.battle)

    def bag_click(self):
        self.click(self.bag)

    def pokemon_click(self):
        self.click(self.pokemon)

    def escape_click(self):
        self.click(self.escape)



class MBar(Mouse):
    def __init__(self):
        super().__init__()
        self.perfume = self.rio['perfume']
        self.spray = self.rio['spray']
        self.sweet_scent = self.rio['sweet_scent']
        self.fish_rod = self.rio['fish_rod']

        self.pokeball = self.rio['pokeball']

    def perfume_click(self):
        self.click(self.perfume)

    def spray_click(self):
        self.click(self.spray)

    def sweet_scent_click(self):
        self.click(self.sweet_scent)

    def fish_rod_click(self):
        self.click(self.fish_rod)

    def pokeball_click(self):
        self.click(self.pokeball)

class MInfoWin(Mouse):
    def __init__(self):
        super().__init__()
        self.iv = self.rio["iv"]
        self.pokedex_cancel = self.rio["pokedex_cancel"]

    def iv_click(self):
        self.click(self.iv)

    def pokedex_cancel_click(self):
        self.click(self.pokedex_cancel)

