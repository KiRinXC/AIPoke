import subprocess
import hashlib
import platform
import sys


def get_machine_code():
    """
    获取机器唯一的特征码 (HWID)
    逻辑：采集 CPUID + 主板序列号 + 系统UUID -> 进行 SHA256 哈希
    """

    # 1. 定义一个执行系统命令的内部函数
    def _get_wmic_output(command):
        try:
            # shell=True 允许执行 shell 命令
            # check_output 获取命令的输出结果
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            # 解码并去除首尾空白
            print(result)
            return result.decode('utf-8', errors='ignore').strip()
        except Exception:
            return ""

    # 2. 采集硬件信息 (针对 Windows 优化)
    system_os = platform.system()
    print(system_os)
    raw_info = ""

    if system_os == "Windows":
        # 获取 CPU ID
        # wmic cpu get processorid -> 得到类似 "ProcessorId \n BFEBFBFF000906EA"
        cpu_id = _get_wmic_output("wmic cpu get processorid")
        print(cpu_id)

        # 获取 主板序列号
        board_id = _get_wmic_output("wmic baseboard get serialnumber")
        print(board_id)

        # 获取 系统 UUID (这是最唯一的标识，类似于电脑的身份证)
        uuid = _get_wmic_output("wmic csproduct get uuid")
        print(uuid)

        # 拼接原始数据
        # 这里的 replace 是为了把多余的空格、换行符全部去掉，只留纯文本
        raw_info = cpu_id + board_id + uuid
        print(raw_info)

    elif system_os == "Linux":
        # Linux 备用方案：读取 machine-id
        try:
            with open("/etc/machine-id", "r") as f:
                raw_info = f.read().strip()
        except:
            # 如果读取失败，回退到 MAC 地址
            import uuid
            raw_info = str(uuid.getnode())

    else:
        # Mac 或其他系统备用方案
        import uuid
        raw_info = str(uuid.getnode())

    # 3. 数据清洗
    # 去除所有空格、换行、制表符，防止格式干扰
    raw_info = "".join(raw_info.split())

    # 如果某种原因获取到的信息太短（比如系统权限被拦截），为了防止空码，加一个默认盐值
    if len(raw_info) < 10:
        raw_info = "UNKNOWN_MACHINE_FALLBACK_" + platform.node()

    # 4. 生成指纹 (哈希)
    # 使用 SHA256 将长短不一的硬件信息变成固定长度的 64位 字符串
    machine_code = hashlib.sha256(raw_info.encode('utf-8')).hexdigest()

    # 通常取前 32 位就足够唯一了，方便用户复制，转大写更美观
    return machine_code[:32].upper()


# --- 测试调用 ---
if __name__ == "__main__":
    print("正在计算机器码...")
    hwid = get_machine_code()
    print("=" * 40)
    print(f"机器码 (HWID): {hwid}")
    print("=" * 40)
    print("请把上面这串代码发给管理员进行授权。")