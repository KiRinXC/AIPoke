import dxcam
class Camera(object):
    def __init__(self):
        self.camera = dxcam.create(output_idx=0, output_color="BGR")
        self.region = (0, 0, 1100, 900)

        self.camera.start(target_fps=10,region=self.region)  # 返回 numpy array (H, W, 3) BGR 格式

    def grab(self):
        frame = self.camera.get_latest_frame()
        return frame