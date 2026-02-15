import logging
import random
import functools
import time

from flet.controls.material import switch
from pywin.dialogs.ideoptions import buttonControlMap

from AIPoke.actor.Key import KOptions, KBar, KInfoWin, KBox
from AIPoke.actor.Mouse import MOptions, MBar, MInfoWin, MBox
from AIPoke.utili.data_manager import CFG_USER
from AIPoke.actor.Random import Random

class Actor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cfg = CFG_USER
        self.rand = Random()
        self.options_prob = self.cfg['options_prob']
        self.bar_prob = self.cfg['bar_prob']
        self.pop_win_prob = self.cfg['pop_win_prob']
        self.skip_iv_prob = self.cfg['skip_iv_prob']
        self.hatch_prob = self.cfg['hatch_prob']
        self.confirm_prob = self.cfg['confirm_prob']

    @classmethod
    def hangup(cls, fn):
        """
        装饰器：在执行按键操作前随机挂起一段时间
        """
        @functools.wraps(fn)
        def wrapper(self, *args, **kw):
            # 注意：这里的 self 是实例 (KOptions 的对象)
            # 必须确保实例中有 self.rand 属性
            delay = self.rand.hangup(0.1, 1, 0.15)
            time.sleep(delay)
            return fn(self, *args, **kw)
        return wrapper

    @classmethod
    def skip(cls, cfg_key):
        """
        装饰器：以 prob 概率直接放弃执行原函数，返回 None
        """
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(self, *args, **kw):
                # 直接从 self.cfg 取值，更加安全稳健
                prob = self.cfg.get(cfg_key, 0.0)
                if random.random() < prob:
                    return None
                return fn(self, *args, **kw)
            return wrapper
        return decorator

    @classmethod
    def view(cls, fn):
        """动作结束后随机停留 1–2 秒再看画面"""
        @functools.wraps(fn)
        def wrapper(self, *args, **kw):
            ret = fn(self, *args, **kw)   # 先执行原函数
            # 停留 0.5–2 秒，内部写死
            delay = self.rand.gauss(0.05,0.4,0.2)
            time.sleep(delay)
            return ret
        return wrapper

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
        self.k_skill_1 = [self.K.battle_press,self.K.battle_press]
        self.k_skill_2 = [self.K.battle_press,self.K.bag_press]

        self.M = MOptions()
        self.m_skill_1 = [self.M.battle_click,self.M.battle_click]
        self.m_skill_2 = [self.M.battle_click,self.M.bag_click]

    @Actor.hangup
    def skill_1(self):
        actors = self.select(self.k_skill_1,self.m_skill_1,"一技能",self.options_prob)
        self.M.random_drift_prob = 0.0
        actors[0]()

        self.M.random_drift_prob = self.M.rio["random_drift_prob"]
        time.sleep(self.rand.hangup(0.02, 0.2, 0.04))
        actors[1]()

    @Actor.hangup
    def skill_2(self):
        actors = self.select(self.k_skill_2,self.m_skill_2,"二技能",self.options_prob)
        self.M.random_drift_prob = 0.0
        actors[0]()

        self.M.random_drift_prob = self.M.rio["random_drift_prob"]
        time.sleep(self.rand.hangup(0.02, 0.2, 0.04))
        actors[1]()
        time.sleep(2)

    @Actor.hangup
    def escape(self):
        self.select(self.K.escape_press, self.M.escape_click,"逃跑" ,self.options_prob)()

    @Actor.hangup
    def cancel(self):
        self.K.press(self.K.B)

class ABar(Actor):
    def __init__(self):
        super().__init__()
        self.K = KBar()
        self.M = MBar()

    @Actor.hangup
    def perfume(self):
        self.select(self.K.perfume_press, self.M.perfume_click,"香水" ,self.bar_prob)()

    @Actor.hangup
    def spray(self):
        self.select(self.K.spray_press, self.M.spray_click,"喷雾" ,self.bar_prob)()

    @Actor.hangup
    def sweet_scent(self):
        self.select(self.K.sweet_scent_press, self.M.sweet_scent_click,"甜甜香气" ,self.bar_prob)()

    @Actor.hangup
    def fish_rod(self):
        self.select(self.K.fish_rod_press, self.M.fish_rod_click,"钓鱼竿" ,self.bar_prob)()

    @Actor.hangup
    def pokeball(self):
        self.select(self.K.pokeball_press,self.M.pokeball_click,"丢球" ,self.bar_prob)()
        time.sleep(3)

class AInfoWin(Actor):
    def __init__(self):
        super().__init__()
        self.K = KInfoWin()
        self.M = MInfoWin()

    @Actor.skip("skip_iv_prob")
    @Actor.hangup
    @Actor.view
    def iv(self):
        self.select(self.K.iv_press, self.M.iv_click, "查看个体值", self.pop_win_prob)()

    @Actor.hangup
    def pokedex_cancel(self):
        self.M.random_drift_prob = 0.0
        self.select(self.K.pokedex_cancel_press, self.M.pokedex_cancel_click, "关闭图鉴", self.pop_win_prob)()
        self.M.random_drift_prob = self.M.rio["random_drift_prob"]

    @Actor.hangup
    def chat_win(self):
        self.select(self.K.chat_win_press, self.M.chat_win_click,"对话", self.pop_win_prob)()

    @Actor.hangup
    def open_chat(self):
        self.K.press(self.K.A)


class ABox(Actor):
    def __init__(self):
        super().__init__()
        self.K = KBox()
        self.M = MBox()

    def K_hatch(self,count,switch,button = "left"):
        self.M.select_pokemon_click(count, switch, button)
        self.K.select_hatch_press()

    def M_hatch(self,count,switch,button = "right"):
        self.M.select_pokemon_click(count, switch, button)
        self.M.select_hatch_click()

    @Actor.hangup
    def hatch_0(self,count):
        self.select(self.K_hatch,self.M_hatch,"选中上栏精灵",self.hatch_prob)(count,0)

    @Actor.hangup
    def hatch_1(self,count):
        self.select(self.K_hatch,self.M_hatch,"选中下栏精灵",self.hatch_prob)(count,1)


    @Actor.hangup
    def select_parent(self):
        self.select(self.K.select_parent_press,self.M.select_parent_click,"选择父母",self.confirm_prob)()

    def hatch(self,count):
        self.hatch_0(count)
        self.hatch_1(count)

    @Actor.hangup
    def confirm_hatch_egg(self):
        self.select(self.K.confirm_hatch_egg_press,self.M.confirm_hatch_egg_click,"确认孵蛋",self.confirm_prob)()

    @Actor.hangup
    def hatch_egg_button(self):
        self.M.hatch_egg_button_click()



