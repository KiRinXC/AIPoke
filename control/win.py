import pygetwindow

def adjust_window():

    # 获取设定的缩放游戏窗口大小
    win_w, win_h = 1100,900

    # 确定游戏界面的左上角起始坐标 并添加至config
    win_x, win_y = 0, 0

    # 获取当前所有已开启的窗口
    windows = pygetwindow.getAllWindows()
    # PokeMMO窗口名称使用了部分西里尔字母进行编码，需要转换成拉丁字母
    trans_table = str.maketrans({
        'Р': 'P',
        'М': 'M',
        'е': 'e',
        'о': 'o'
    })
    for window in windows:
        # 将窗口的字符转换后在进行比较
        title_trans = window.title.translate(trans_table)
        if title_trans == "PokeMMO":
            # 激活窗口并调整大小和位置
            window.activate()
            window.resizeTo(win_w, win_h)
            window.moveTo(win_x, win_y)
            return window
    return False