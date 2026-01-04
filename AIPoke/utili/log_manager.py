import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from AIPoke.utili.path_manager import LOG_DIR


def init_logging(is_debug=False):
    """
    配置全局日志系统
    :param is_debug: bool, 是否开启控制台输出
    :return: logger 对象
    """
    # 获取根记录器 (Root Logger)
    # 使用根记录器的好处是，项目中引用的第三方库(如 requests)的日志也能被捕获
    logger = logging.getLogger()

    # 防止重复添加 Handler (关键！)
    # 如果 logger 已经有处理器了，说明已经初始化过，直接返回，防止打印两条日志
    if logger.hasHandlers():
        return logger

    # 设置默认级别为 INFO
    logger.setLevel(logging.INFO)

    # 3. 定义日志格式 (满足你想要的时间+等级)
    # 格式示例: 2023-10-27 10:30:01 - [INFO] - [MainThread] - 任务启动成功
    log_formatter = logging.Formatter(
        fmt='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件处理器 (按天切割，保留7天)
    log_file_path = os.path.join(LOG_DIR, 'AIPoke.log')

    try:
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when='midnight',  # 每天午夜切割
            interval=1,  # 间隔 1 天
            backupCount=7,  # 保留 7 个旧文件
            encoding='utf-8'  # 强制 UTF-8，防止中文乱码
        )
        file_handler.setFormatter(log_formatter)
        file_handler.suffix = "%Y-%m-%d.log"  # 设置切割后的后缀
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"日志文件创建失败: {e}")

    # 控制台处理器 (Debug 模式才开启)
    if is_debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    return logger