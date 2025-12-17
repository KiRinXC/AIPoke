import os
import json
import rsa
import glob
import logging
import base64
import datetime
import uuid
from utili.path_manager import KEY_DIR
from key.uid import UID

class ClientKeyManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pub_file = os.path.join(KEY_DIR, 'public.pem')
        self.pubkey = None

        try:
            with open(self.pub_file, 'rb') as f:
                self.pubkey = rsa.PublicKey.load_pkcs1(f.read())
        except Exception as e:
            self.logger.error(f"公钥加载失败，无法验证密钥: {e}")

        self.uid = UID().get_uid()

    def _verify_key(self, key_str):
        """
        [内部函数] 验证单行密钥字符串
        :param key_str: 一行加密的字符串
        :return: (dict) payload 数据 或 None
        """
        if not key_str or not self.pubkey:
            return None

        try:
            # 1. Base64 解包
            # 可能会因为复制粘贴多余空格导致报错，先 strip
            wrapper_json = base64.b64decode(key_str.strip()).decode('utf-8')
            wrapper = json.loads(wrapper_json)

            msg_str = wrapper['msg']  # 明文 Payload
            sign_b64 = wrapper['sign']  # 签名

            # 2. RSA 验签
            rsa.verify(
                msg_str.encode('utf-8'),
                base64.b64decode(sign_b64),
                self.pubkey
            )

            # 3. 解析 Payload
            payload = json.loads(msg_str)
            return payload

        except Exception as e:
            return None

    def get_active_permissions(self):
        """
        【核心功能】加载所有密钥，计算出当前拥有的最大权限
        :return: (dict) 格式: {'App_A': '2025-12-31', 'App_B': '2024-10-01'}
        """
        # 最终结果字典: { 'app_type': 'max_expire_date_str' }
        active_permissions = {}

        # 1. 扫描所有 txt 文件
        pattern = os.path.join(KEY_DIR, "*.txt")
        files = glob.glob(pattern)

        if not files:
            self.logger.warning(f"在 {KEY_DIR} 下未找到任何 .txt 密钥文件")
            return {}

        # 2. 遍历文件
        for file_path in files:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    key_content = f.read().strip()
                if not key_content:
                    self.logger.warning(f"发现空密钥文件 [{file_name}]，正在删除...")
                    os.remove(file_path)
                    continue
                payload = self._verify_key(key_content)

                # --- 情况 A: 密钥无效 (签名错误/格式错误) ---
                if not payload:
                    self.logger.error(f"密钥无效或格式损坏 [{file_name}]，正在删除...")
                    os.remove(file_path)
                    continue
                # --- 情况 B: 机器码 (UID) 不匹配 ---
                if payload.get('uid') != self.uid:
                    self.logger.error(f"密钥不属于本机 (UID不匹配) [{file_name}]，正在删除...")
                    os.remove(file_path)
                    continue

                # --- 情况 C: 有效密钥，进行处理 ---
                app = payload.get('app')
                expire = payload.get('expire')

                # --- 聚合逻辑 (取最大日期) ---

                # 将字符串转为 datetime 对象方便比较
                new_expire_dt = datetime.datetime.strptime(expire, "%Y-%m-%d")
                # 当前时间
                now = datetime.datetime.now()
                # 判断过期：如果 当前时间 > 过期日期的第二天0点，则视为彻底过期
                if now > (new_expire_dt + datetime.timedelta(days=1)):
                    self.logger.warning(f"密钥已过期 (到期: {expire}) [{file_name}]，正在删除...")
                    os.remove(file_path)
                    continue
                # 如果字典里已经有这个功能的日期了，比较谁更大
                if app in active_permissions:
                    # 如果字典里已经有这个功能的日期了，比较谁更大
                    current_max_str = active_permissions[app]
                    current_max_dt = datetime.datetime.strptime(current_max_str, "%Y-%m-%d")

                    if new_expire_dt > current_max_dt:
                        active_permissions[app] = expire
                        self.logger.info(f"更新权限 [{app}] 到新日期: {expire}")
                else:
                    # 第一次遇到这个功能
                    active_permissions[app] = expire

            except Exception as e:
                self.logger.error(f"处理文件 {file_path} 时发生未知错误: {e}")

        return active_permissions

    def save_key(self, key):
        """
        【保存功能】将用户输入的新密钥保存为随机文件
        :param key: 管理员发来的加密字符串
        :return: (bool, msg)
        """
        if not key or len(key) < 10:
            return False

        # 1. 先验证一下这个 Key 是否有效 (是本机吗？签名对吗？)
        payload = self._verify_key(key)

        if not payload:
            self.logger.error("密钥无效（签名错误或格式损坏）")
            return False

        if payload.get('uid') != self.uid:
            self.logger.error(f"该密钥不属于此机器")
            return False

        # 2. 生成随机文件名
        # 使用 UUID 防止文件名冲突，后缀用 .txt
        filename = f"{uuid.uuid4().hex[:16]}.txt"
        file_path = os.path.join(KEY_DIR, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(key)

            self.logger.info(f"新密钥已保存至: {filename}")

            # 返回成功信息，顺便告诉用户这个 Key 是啥功能的
            return True, payload.get('app'),payload.get('expire')

        except Exception as e:
            self.logger.error(f"保存密钥文件失败: {e}")
            return False
