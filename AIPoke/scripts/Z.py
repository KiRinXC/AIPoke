import time
from enum import Enum,IntEnum

from AIPoke.scripts.A import AIPoke
from AIPoke.utili.log_manager import init_logging

# --- 状态位掩码定义---
class StateMap(IntEnum):
    # 组合状态（如果有）可以在此扩展
    PASS_ANIM = 0b0000  # 过场动画/等待中
    POP_WIN   = 0b0001  # 弹窗/疑似闪光
    ESCAPE    = 0b0010  # 逃跑/选项框 (代表到了玩家操作回合)
    NICKNAME  = 0b0100  # 脱战/漫游状态 (可以看到昵称)
    POKEDEX   = 0b1000  # 弹出图鉴

# 血条处的信息
class INFO(IntEnum):
    NOTHING = 0b000  # 啥也没/群怪
    HP_BAR  = 0b001  # 有血条
    DITTO   = 0b010  # 是目标精灵
    ZZZ     = 0b100  # 睡着了
    CATCH   = 0b111  # 丢球
    SKILL   = 0b011  # 需要睡眠


# --- 内部捕捉阶段记录 ---
class CaptureStage(Enum):
    MEET = 0  # 刚见面
    HP_LOWERED = 1  # 已经打过一技能（修血）
    SLEEPING = 2  # 已经打过二技能（催眠）
    # 之后就是一直扔球，维持在 SLEEPING 阶段即可


class Z(AIPoke):
    def __init__(self):
        super().__init__()
        self.capture_stage = CaptureStage.MEET  # 内部状态：记录当前抓到哪一步了

    def update_state(self, frame):
        """返回当前画面的状态码"""
        is_nickname = self.detector.det_nickname(frame)
        is_escape = self.detector.det_escape(frame)
        is_pop_win = self.detector.det_pop_win(frame)
        is_pokedex = self.detector.det_pokedex(frame)

        # 组合位掩码
        state = (is_pokedex << 3) | (is_nickname << 2) | (is_escape << 1) | is_pop_win

        self.state_queue.append(state)
        return state

    def update_info(self, frame):
        """返回血条信息"""
        # 视觉状态检测
        is_hp_bar = self.detector.det_hp_bar(frame)
        is_ditto = self.detector.det_poke_ditto(frame)
        is_zzz = self.detector.det_zzz(frame)
        info = (is_zzz << 2) | (is_ditto << 1) | is_hp_bar

        return info

    def run(self):
        while True:
            # 1. 获取所有传感器数据
            frame = self.camera.grab()
            state = self.update_state(frame)
            info = self.update_info(frame)

            # 3. 核心决策逻辑 (Reactive Logic)

            # --- 优先级 1: 异常与成功处理 ---
            # if is_pop_win:
            #     # 检测到弹窗 -> 报警
            #     self.action_alert()
            #     continue

            if state == StateMap.PASS_ANIM:
                # 检测到图鉴 -> 捕捉成功
                print("点取消")

            elif state == StateMap.NICKNAME:
                print("人物移动")

            # --- 优先级 3: 战斗操作状态 (必须看到 escape 按钮才操作) ---
            elif state == StateMap.ESCAPE:
                # 操作只在逃跑处
                self.catch(info)

            elif state == StateMap.POP_WIN:
                self.logger.warning("疑似闪光")
                if self.check_shiny(StateMap.POP_WIN):
                    self.shiny_reminder()

            elif state == StateMap.POKEDEX:
                print("图鉴，点取消")

            else:
                self.alert_reminder()

            time.sleep(0.1)

    def catch(self, info,poke_flags, is_hp_bar, is_ditto, is_zzz):
        """
        处理战斗回合的逻辑
        不需要等待，只做当前最应该做的一个动作
        """
        # 情况 A: 群怪 (没有血条) 或 非百变怪
        # 逻辑：(没血条) 或 (有血条但不是百变怪) -> 逃跑
        if info == INFO.NOTHING or info == INFO:
            print(f"[{bin(poke_flags)}] 非目标/群怪 -> 点击逃跑")
            self.click_escape()
            self.capture_stage = CaptureStage.MEET  # 重置状态
            return

        # 情况 B: 是百变怪 (有血条 且 是百变怪)
        if is_hp_bar and is_ditto:
            # 根据内部记录的阶段，决定出什么招

            # 阶段 1: 刚见面 -> 打一技能 (修血)
            if self.capture_stage == CaptureStage.MEET:
                print(f"[{bin(poke_flags)}] 发现百变怪 -> 使用技能1 (修血)")
                self.use_skill_1()
                self.capture_stage = CaptureStage.HP_LOWERED  # 状态流转
                return

            # 阶段 2: 已经修血 -> 打二技能 (催眠)
            if self.capture_stage == CaptureStage.HP_LOWERED:
                print(f"[{bin(poke_flags)}] 血量已压低 -> 使用技能2 (催眠)")
                self.use_skill_2()
                self.capture_stage = CaptureStage.SLEEPING  # 状态流转
                return

            # 阶段 3: 已经催眠过 -> 检查是否睡着 -> 扔球 或 补催眠
            if self.capture_stage == CaptureStage.SLEEPING:
                if is_zzz:
                    print(f"[{bin(poke_flags)}] 目标睡眠中 -> 扔球")
                    self.throw_ball()
                    # 扔球后状态不变，如果没抓到下一轮还会进这里
                else:
                    print(f"[{bin(poke_flags)}] 目标醒了/未睡着 -> 补技能2")
                    self.use_skill_2()
                return

    # --- 动作封装 (模拟点击) ---
    def action_roaming(self):
        # print("正在寻找宝可梦...")
        self.capture_stage = CaptureStage.MEET  # 确保重置战斗状态
        # move_character() # 这里调用你的移动函数

    def action_success(self):
        print("!!! 捕捉成功 (Pokedex) !!!")
        # press_space() # 按空格退出图鉴
        self.capture_stage = CaptureStage.MEET  # 重置
        time.sleep(1)  # 稍作防抖

    def action_alert(self):
        print("!!! 出现弹窗异常 !!!")
        # send_message()

    def click_escape(self):
        # 点击屏幕上的逃跑按钮
        pass

    def use_skill_1(self):
        # 点击技能1
        pass

    def use_skill_2(self):
        # 点击技能2
        pass

    def throw_ball(self):
        # 点击背包 -> 球 -> 扔
        pass


if __name__ == '__main__':
    init_logging(is_debug=True)
    bot = Z()
    bot.run()