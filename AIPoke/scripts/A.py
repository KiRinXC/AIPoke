from collections import deque
import logging
import threading

from AIPoke.actor.Actor import AOptions,ABar,AInfoWin
from AIPoke.image.Camera import Camera
from AIPoke.detect.Detect import Detect
from AIPoke.utili.reminder import Reminder

class AIPoke:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.options = AOptions()
        self.bar = ABar()
        self.infowin = AInfoWin()
        self.reminder = Reminder()
        self.detector = Detect()
        self.camera = Camera()
        self.state_queue = deque([0] * 10, maxlen=10)  # 闪光判定队列
        self.quit_event = threading.Event()
        self.quit_event.clear()

    def check_shiny(self,state):
        """检查队列是否全为闪光编码 (疑似闪光)"""
        if all(v == state for v in self.state_queue):
            return True
        return False


    def alert_reminder(self):
        self.reminder.send_alert_remind()
        self.reminder.screen_shot(self.camera.grab())
        self.state_queue.clear()
        exit()

    def shiny_reminder(self):
        self.reminder.send_shiny_remind()
        self.reminder.screen_shot(self.camera.grab())
        self.state_queue.clear()
        exit()