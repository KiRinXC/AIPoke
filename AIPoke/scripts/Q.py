from collections import deque
import time

from AIPoke.actor.Actor import ABar,AOptions
from AIPoke.image.Camera import Camera
from AIPoke.detect.Detect import Detect
from AIPoke.utili.reminder import Reminder
from AIPoke.utili.log_manager import init_logging


STATE_MAP = {
    0b000: '过场动画',
    0b100: '脱战',
    0b010: '弹出选项框',
    0b001: '可能出闪',
}

QUEUE_LEN = 10          # 记录连续 10 帧
results = [0]

if __name__ == '__main__':
    init_logging(is_debug=True)
    camera = Camera()
    detector = Detect()
    options = AOptions()
    bar = ABar()
    reminder = Reminder()
    time.sleep(1)
    q = deque([0] * QUEUE_LEN, maxlen=QUEUE_LEN)   # 预填 0，保证一开始就满

    while True:
        frame = camera.grab()
        is_nickname = detector.det_nickname(frame)
        is_escape   = detector.det_escape(frame)
        is_pop_win  = detector.det_pop_win(frame)
        key = (is_nickname << 2) | (is_escape << 1) | is_pop_win
        if key != results[-1]:
            results.append(key)
            if key == 0b000:
                pass
            elif key == 0b100:
                bar.sweet_scent()
                time.sleep(9)
            elif key == 0b010:
                options.escape()
                time.sleep(1)
            elif key == 0b001:
                    print("疑似出闪")
            else:
                reminder.send_alert_remind()
                reminder.screen_shot(frame)
                print(f"key={key:0b}游戏异常")
                q.clear()
                exit()

        if all(v == 0b001 for v in q):
            reminder.send_shiny_remind()
            reminder.screen_shot(frame)
            print("出闪")
            q.clear()
            exit()
        q.append(key)
