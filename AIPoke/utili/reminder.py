from urllib import request, parse
from datetime import datetime
import logging
import cv2

from AIPoke.utili.data_manager import CFG_USER
class Reminder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.shiny_code = CFG_USER["shiny_code"]
        self.alert_code = CFG_USER["alert_code"]

    def get_info(self):
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        info = f"{year}-{month}-{day}-{hour}-{minute}"
        return info

    def send_shiny_remind(self):
        """
        发送提醒
        """
        # 再发喵提醒
        request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id": self.shiny_code, "text": self.get_info()}))
        self.logger.info("---已发送出闪喵提醒---")

    def send_alert_remind(self,text="游戏异常,需要自检"):

        # 再发喵提醒
        request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id": self.alert_code, "text": text}))
        self.logger.error("---已发送异常喵提醒---")

    def screen_shot(self,frame):
        # 使用 OpenCV 保存图像
        cv2.imwrite(f'{self.get_info()}.png', frame)



