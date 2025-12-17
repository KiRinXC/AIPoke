import sys
import os

def get_root():
    """
    智能获取项目根目录
    1. 如果是打包后的 exe 运行：返回 exe 所在文件夹
    2. 如果是代码运行：返回 项目根目录 (即 AIPoke 文件夹)
    """
    # sys.frozen 是 PyInstaller 打包后会自动添加的属性
    if getattr(sys, 'frozen', False):
        # --- 打包环境 (Exe) ---
        # sys.executable 是 exe 文件的绝对路径
        # dirname 拿到的是 exe 所在的文件夹
        base_path = os.path.dirname(sys.executable)
    else:
        # --- 开发环境 (PyCharm / 代码) ---
        # __file__ 是当前脚本(paths.py)的路径: .../AIPoke/utili/paths.py
        # 第一次 dirname: .../AIPoke/utili
        # 第二次 dirname: .../AIPoke (回到根目录)
        current_path = os.path.abspath(__file__)
        base_path = os.path.dirname(os.path.dirname(current_path))
    data_dir = os.path.join(base_path, 'data')
    return data_dir

def init_dir():
    """
    初始化项目文件夹结构
    """
    # 把需要创建的文件夹放入一个列表，方便管理
    folders_to_create = [
        LOG_DIR,
        DATA_DIR,
        KEY_DIR
    ]

    for folder in folders_to_create:
        try:
            # exist_ok=True: 如果文件夹已存在，静默跳过；不存在则创建
            os.makedirs(folder, exist_ok=True)
        except PermissionError:
            print(f"[严重错误] 无法创建目录: {folder}，请尝试以管理员身份运行或更换目录。")


# 预定义一些常用路径，供其他模块直接调用
ROOT_DIR = get_root()
LOG_DIR = os.path.join(ROOT_DIR, "LOGS")
DATA_DIR = os.path.join(ROOT_DIR, "DATA")
KEY_DIR = os.path.join(ROOT_DIR, "KEY")
TEM_DIR = os.path.join(ROOT_DIR, "TEM")