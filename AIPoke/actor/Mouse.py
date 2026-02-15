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
        self.chat_win = self.rio["chat_win"]

    def iv_click(self):
        self.click(self.iv)

    def pokedex_cancel_click(self):
        self.click(self.pokedex_cancel)

    def chat_win_click(self):
        self.click(self.chat_win)


class MBox(Mouse):
    def __init__(self):
        super().__init__()
        self.first_pokemon_in_box = self.rio["first_pokemon_in_box"]
        self.box_spacing = self.rio["box_spacing"]
        self.hatch_grid = self.rio["hatch_grid"]
        self.hatch_egg_button = self.rio["hatch_egg_button"]
        self.confirm_hatch_egg = self.rio["confirm_hatch_egg"]
        self.select_parent = self.rio["select_parent"]

    def select_pokemon_click(self,count,switch,button='left'):
        row = count / 10
        column = count % 10
        x = self.first_pokemon_in_box[0]+ column * self.box_spacing[0]
        y = self.first_pokemon_in_box[1]+ (row + switch * 3) * self.box_spacing[1]
        rio = [x,y,self.first_pokemon_in_box[2],self.first_pokemon_in_box[3]]
        self.click(rio,button)

    def select_parent_click(self):


    def select_hatch_click(self):
        position = pydirectinput.position()
        roi = [position[0]+self.hatch_grid[0],position[1]+self.hatch_grid[1],self.hatch_grid[2],self.hatch_grid[3]]
        self.click(roi)

    def hatch_egg_button_click(self):
        self.click(self.hatch_egg_button)

    def confirm_hatch_egg_click(self):
        self.click(self.confirm_hatch_egg)

