import math
import random
import time
import numpy as np
import pydirectinput
import pyautogui

# ================= 全局配置 =================
pydirectinput.PAUSE = 0.0
pydirectinput.FAILSAFE = True


class Point:
    def __init__(self):
        pass
    def _get_control_points(self, start_x, start_y, end_x, end_y, distortion=0.3):
        """
        生成控制点，支持一定的扭曲度
        """
        dist = math.hypot(end_x - start_x, end_y - start_y)
        offset = min(dist * distortion, 200)

        rx1 = random.randint(int(-offset), int(offset))
        ry1 = random.randint(int(-offset), int(offset))
        rx2 = random.randint(int(-offset), int(offset))
        ry2 = random.randint(int(-offset), int(offset))

        p1 = (start_x + (end_x - start_x) / 3 + rx1, start_y + (end_y - start_y) / 3 + ry1)
        p2 = (start_x + 2 * (end_x - start_x) / 3 + rx2, start_y + 2 * (end_y - start_y) / 3 + ry2)
        return p1, p2

    def _bezier_curve(self, p0, p1, p2, p3, t):
        """ 三阶贝塞尔 """
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        return x, y

    def _generate_path(self, start, end, speed_factor=1.0):
        """
        生成路径点
        speed_factor: 越大点越少（越快）
        """
        x1, y1 = start
        x2, y2 = end
        dist = math.hypot(x2 - x1, y2 - y1)

        # 基础步数：距离越远步数越多，但整体要快
        # base_steps 越小，移动越快
        base_steps = int(max(8, int(dist / (30 * speed_factor))))

        p1, p2 = self._get_control_points(x1, y1, x2, y2)

        path = []
        # 使用 Ease-Out (sin) 曲线，让末端减速
        t_vals = np.sin(np.linspace(0, np.pi / 2, base_steps))

        for t in t_vals:
            bx, by = self._bezier_curve((x1, y1), p1, p2, (x2, y2), t)
            path.append((int(bx), int(by)))

        return path

    def _calculate_offset_target(self, start_x, start_y, dest_x, dest_y):
        """
        计算过冲点（虚假目标）
        """
        dist = math.hypot(dest_x - start_x, dest_y - start_y)

        # 1. 距离过近不触发过冲，否则很怪
        if dist < 50:
            return dest_x, dest_y

        # 2. 计算向量
        vec_x = dest_x - start_x
        vec_y = dest_y - start_y

        # 3. 过冲比例：距离越远，过冲比例越小（但绝对距离可能较大）
        # 随机 3% 到 8% 的过冲
        overshoot_ratio = random.uniform(0.95, 1.05)
        # 4. 计算假目标坐标 (沿向量延伸)
        fake_x = start_x + vec_x * overshoot_ratio
        fake_y = start_y + vec_y * overshoot_ratio

        # 5. 增加一点侧向偏差 (不止是冲过头，还会偏一点)
        # 模拟“手滑”
        lateral_error = random.randint(-10, 10)
        fake_x += lateral_error
        fake_y += lateral_error

        return int(fake_x), int(fake_y)

    def move_to(self, x,y):
        start_x, start_y = pyautogui.position()

        # Step 1: 计算过冲点
        fake_x, fake_y = self._calculate_offset_target(start_x, start_y, x, y)

        # 如果计算出的假目标和真目标一样（距离太近），就只走一段
        is_overshoot = (fake_x != x or fake_y != y)

        # Step 2: 生成第一段轨迹 (起点 -> 过冲点)
        # speed_factor=1.2 表示这段稍微快一点，模拟爆发
        path1 = self._generate_path((start_x, start_y), (fake_x, fake_y), speed_factor=1.2)

        # 执行第一段
        for px, py in path1:
            pydirectinput.moveTo(px, py, _pause=False)
            time.sleep(0.0015)  # 极速

        if is_overshoot:
            # === 关键细节：反应延迟 ===
            # 到达过冲点后，人脑意识到“过头了”，肌肉刹车需要时间
            # 这是一个极短的停顿，是拟人的精髓
            time.sleep(random.uniform(0.02, 0.09))

            # Step 3: 生成第二段轨迹 (过冲点 -> 真目标)
            # 这一段是“修正”，要慢、要准
            curr_x, curr_y = pyautogui.position()
            # speed_factor=0.6 表示这段比较慢
            path2 = self._generate_path((curr_x, curr_y), (x, y), speed_factor=0.6)

            for px, py in path2:
                pydirectinput.moveTo(px, py, _pause=False)
                # 修正阶段稍微慢一点
                time.sleep(0.003)

    def shake_drift(self,prob):
        """
        模拟松开鼠标后的微小位移（生理性漂移）
        """
        # 1. 不是每次都漂移，给个概率 (例如 70%)
        if random.random() > prob:
            return

        # 2. 漂移距离极短，通常在 1-4 像素之间
        # 使用高斯分布，让 drift 主要集中在小范围
        drift_x = int(random.uniform(-20, 20))
        drift_y = int(random.uniform(-20, 20))

        # 过滤掉 0 移动
        if drift_x == 0 and drift_y == 0:
            return

        # 3. 执行相对移动 (Relative Move)
        # 这种微小的移动不需要贝塞尔曲线，直接 sensor jump 即可，非常真实
        pydirectinput.moveRel(drift_x, drift_y, relative=True, _pause=False)


    def random_drift(self,prob):
        """
        模拟鼠标在完成动作后随机漂移
        """
        if random.random() > prob:
            return
        # 随机漂移的目标点
        drift_x = int(random.uniform(0, 1100))
        drift_y = int(random.uniform(0, 900))

        self.move_to(drift_x, drift_y)





