import os
import cv2

def load_all_templates(template_dir):
    """
    【通用预加载】
    遍历指定目录，加载所有图片模板到内存字典中。

    参数:
        template_dir: 模板文件夹路径 (例如 "../data/TEM")

    返回:
        dict: { "文件名(无后缀)": numpy数组, ... }
        例如: { "escape": img_data, "attack": img_data }
    """
    templates = {}

    # 1. 路径检查
    if not os.path.exists(template_dir):
        print(f"[错误] 模板目录不存在: {template_dir}")
        return templates

    # 支持的图片格式
    valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']

    # 2. 遍历文件夹
    for filename in os.listdir(template_dir):
        # 分离文件名和后缀
        name, ext = os.path.splitext(filename)

        # 检查是否是图片
        if ext.lower() in valid_extensions:
            full_path = os.path.join(template_dir, filename)

            # 3. 加载图片 (必须是灰度模式 0)
            img = cv2.imread(full_path, 0)

            if img is not None:
                # 存入字典，Key 是文件名（不带后缀）
                templates[name] = img
                print(f" [OK] 已加载: {name} ({img.shape})")
            else:
                print(f" [Fail] 无法读取图片: {filename}")

    print(f"--- 模板加载完毕，共 {len(templates)} 个 ---")
    return templates
