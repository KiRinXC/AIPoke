"""群怪刷闪"""
import time
from enum import IntEnum

from AIPoke.scripts.A import AIPoke
from AIPoke.utili.log_manager import init_logging


# --- 常量定义 ---
class StateMap(IntEnum):
    PASS_ANIM = 0b000  # 过场动画/等待
    NICKNAME = 0b100  # 脱战/漫游状态 (可以看到昵称)
    ESCAPE = 0b010  # 战斗菜单 (可以看到逃跑/Fight)
    POP_WIN = 0b001  # 弹窗/疑似闪光
    # 组合状态（如果有）可以在此扩展

class Q(AIPoke):
    def __init__(self):
        super().__init__()

    def update_state(self, frame):
        """核心视觉感知层：返回当前画面的状态码"""
        is_nickname = self.detector.det_nickname(frame)
        is_escape = self.detector.det_escape(frame)
        is_pop_win = self.detector.det_pop_win(frame)

        # 组合位掩码
        state = (is_nickname << 2) | (is_escape << 1) | is_pop_win

        self.state_queue.append(state)
        return state

    def run(self):
        """主循环"""
        while not self.quit_event.is_set():
            frame = self.camera.grab()
            state = self.update_state(frame)

            # 如果是脱战状态 (在野外)
            if state == StateMap.PASS_ANIM:
                # 动画中不做任何事
                pass

            elif state == StateMap.NICKNAME:
                self.bar.sweet_scent()
                time.sleep(9)

            # 如果是战斗状态 (出现了选项框)
            elif state == StateMap.ESCAPE:
                self.options.escape()

            # 如果是疑似闪光 (但还没填满队列)
            elif state == StateMap.POP_WIN:
                self.logger.warning("疑似闪光")
                if self.check_shiny(StateMap.POP_WIN):
                    self.shiny_reminder()
            # 异常状态
            else:
                self.alert_reminder()

            # 循环末尾小睡，防止过度占用 CPU
            time.sleep(0.1)


if __name__ == '__main__':
    init_logging(is_debug=True)

    # 启动前的缓冲
    print("脚本将在 3 秒后启动，请切换至游戏窗口...")
    time.sleep(3)

    # 实例化并运行
    bot = Q()
    bot.run()