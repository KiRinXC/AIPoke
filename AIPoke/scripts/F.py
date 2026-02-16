"""孵蛋"""
import time
from enum import IntEnum

from AIPoke.scripts.A import AIPoke
from AIPoke.utili.log_manager import init_logging


# --- 常量定义 ---
class StateMap(IntEnum):
    PASS_ANIM = 0b0000  # 过场动画/等待
    CHAT_WIN = 0b0001 # 存在对话
    SELECT_PARENT = 0b0010  # 开始孵蛋，可以选择父母
    OPEN_BOX = 0b0100 # 打开电脑箱子
    HATCH = 0b1000  # 点击孵蛋


class F(AIPoke):
    def __init__(self,boxes):
        super().__init__()
        self.fishing = False
        self.boxes = boxes

    def update_state(self, frame):
        """核心视觉感知层：返回当前画面的状态码"""
        is_nickname = self.detector.det_nickname(frame)
        is_chat_win = self.detector.det_chat_win(frame)
        is_select_parent = self.detector.det_select_parent(frame)
        is_computer_box = self.detector.det_computer_box(frame)
        is_hatch_egg_button = self.detector.det_hatch_egg_button(frame)

        # 组合位掩码
        state = (is_hatch_egg_button << 3) | (is_computer_box << 2) | (is_select_parent << 1) | is_chat_win

        self.state_queue.append(state)
        return state,is_nickname

    def run(self):
        """主循环"""
        count = 0
        box_num = 0
        while not self.quit_event.is_set():
            frame = self.camera.grab()
            state,is_nickname = self.update_state(frame)
            print(bin(state),is_nickname)
            # 如果是脱战状态 (在野外)
            if state == StateMap.PASS_ANIM and not is_nickname:
                # 动画中不做任何事
                pass
            # 进行对话
            elif state == StateMap.CHAT_WIN:
                self.infowin.chat_win()

            # 可以选择父母了
            elif state == StateMap.SELECT_PARENT:
                self.box.select_parent()

            # 打开了电脑箱子
            elif state == StateMap.OPEN_BOX:
                if count == 30:
                    print("切换箱子")
                    count = 0
                    break
                self.box.hatch(count)
                count+=1
                time.sleep(1)

            elif state == StateMap.HATCH:
                self.box.hatch_egg_button()
                self.box.confirm_hatch_egg()

            elif is_nickname:
                self.infowin.open_chat()
            else:
                self.reminder.send_alert_remind("未知错误")
            time.sleep(0.1)

if __name__ == '__main__':
    init_logging(is_debug=True)

    # 启动前的缓冲
    print("脚本将在 3 秒后启动，请切换至游戏窗口...")
    time.sleep(3)

    # 实例化并运行
    bot = F(1)
    bot.run()