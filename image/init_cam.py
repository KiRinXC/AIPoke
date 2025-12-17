import dxcam

def init_cam():
    camera = dxcam.create(output_idx=0, output_color="BGR")
    region = (0, 0, 1100, 900)

    camera.start(target_fps=10,region=region)  # 返回 numpy array (H, W, 3) BGR 格式
    return camera