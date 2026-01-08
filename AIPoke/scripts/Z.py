import time
from enum import Enum,IntEnum
import threading

from AIPoke.scripts.A import AIPoke
from AIPoke.move.move import Walker
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
    SKILL   = 0b011  # 是目标精灵，但是未睡眠     需要催眠/磨血
    CATCH   = 0b111  # 是目标精灵，且睡着了       直接捕捉


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
        self.walker = Walker()
        self.move_event = threading.Event()
        self.move_event.clear()
        self.obs_event = threading.Event()
        self.obs_event.clear()

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

    def detect(self):
        while not self.quit_event.is_set():
            # 1. 获取所有传感器数据
            frame = self.camera.grab()
            state = self.update_state(frame)
            info = self.update_info(frame)
            is_obs = self.detector.det_obs(frame,["left","right"])

            if state == StateMap.PASS_ANIM:
                self.move_event.clear()

            elif state == StateMap.NICKNAME:
                self.move_event.set()
                self.obs_event.set() if is_obs else self.obs_event.clear()
                # print("人物移动")

            # --- 优先级 3: 战斗操作状态 (必须看到 escape 按钮才操作) ---
            elif state == StateMap.ESCAPE:
                # 操作只在逃跑处
                self.catch(info)

            elif state == StateMap.POP_WIN:
                self.logger.warning("疑似闪光")
                if self.check_shiny(StateMap.POP_WIN):
                    self.shiny_reminder()
                    self.quit_event.set()

            elif state == StateMap.POKEDEX:
                self.capture_stage = CaptureStage.MEET
                self.infowin.iv()
                self.infowin.pokedex_cancel()

            else:
                self.alert_reminder()
                self.quit_event.set()
            time.sleep(0.1)

    def catch(self, info):
        """
        处理战斗回合的逻辑
        不需要等待，只做当前最应该做的一个动作
        """

        # 百变怪没睡着
        if info == INFO.SKILL:
            # 阶段 1: 刚见面 -> 打一技能 (修血)
            if self.capture_stage == CaptureStage.MEET:
                self.options.skill_1()
                self.capture_stage = CaptureStage.HP_LOWERED  # 状态流转
                time.sleep(5)
                return
            # 阶段 2: 已经修血 -> 打二技能 (催眠)
            elif self.capture_stage == CaptureStage.HP_LOWERED:
                self.options.skill_2()
                self.capture_stage = CaptureStage.SLEEPING
                return
            else:
                self.logger.error(f"出现未知路径: {self.capture_stage}")
                self.alert_reminder()
                self.quit_event.set()

        elif info == INFO.CATCH:
            # 阶段 3: 已经修血且睡眠 -> 扔球
            self.bar.pokeball()
            self.capture_stage = CaptureStage.HP_LOWERED  # 重置状态
            return
        else:
            self.options.escape()
            return

    def move(self):
        """移动线程"""
        while not self.quit_event.is_set():
            # 在尝试移动前，先阻塞等待！
            # 如果 move_event 是 clear 状态（遇怪中），线程会在这里彻底挂起（休眠），
            # CPU 占用率为 0%，直到 detect 线程再次 set 它。
            self.move_event.wait()

            # 只有允许移动时，才进入具体的移动逻辑
            if not self.quit_event.is_set():
                self.walker.patrol_x(self.move_event, self.obs_event, [5, 20])

    def run(self):
        """主入口：启动双线程"""
        # 创建线程
        t_detect = threading.Thread(target=self.detect, name="Thread-Detect")
        t_move = threading.Thread(target=self.move, name="Thread-Move")

        # 设置为守护线程 (Daemon)
        # 这样当你强制关闭主程序（或 Ctrl+C）时，子线程会自动随之关闭，不会卡在后台
        t_detect.daemon = True
        t_move.daemon = True

        # 启动
        t_detect.start()
        t_move.start()
        # 主线程阻塞等待
        try:
            while not self.quit_event.is_set():
                # 每秒检查一次子线程是否还活着
                if not t_detect.is_alive() or not t_move.is_alive():
                    self.logger.error("检测到子线程意外退出，脚本终止")
                    self.quit_event.set()
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("用户手动停止")
            self.quit_event.set()

        # 等待子线程结束
        t_detect.join()
        t_move.join()

if __name__ == '__main__':
    init_logging(is_debug=True)
    bot = Z()
    time.sleep(2)
    bot.run()