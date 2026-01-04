import rsa
import base64
import json
import os
import datetime
from AIPoke.utili.path_manager import KEY_DIR


class AdminKeyGenerator:
    def __init__(self):
        self.priv_file = os.path.join(KEY_DIR, 'private.pem')
        self.pub_file = os.path.join(KEY_DIR, 'public.pem')
        self.privkey = None
        self.pubkey = None
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """加载或生成 RSA 密钥对"""
        if os.path.exists(self.priv_file) and os.path.exists(self.pub_file):
            with open(self.priv_file, 'rb') as f:
                self.privkey = rsa.PrivateKey.load_pkcs1(f.read())
            with open(self.pub_file, 'rb') as f:
                self.pubkey = rsa.PublicKey.load_pkcs1(f.read())
        else:
            (self.pubkey, self.privkey) = rsa.newkeys(2048)

            with open(self.priv_file, 'wb') as f:
                f.write(self.privkey.save_pkcs1())
            with open(self.pub_file, 'wb') as f:
                f.write(self.pubkey.save_pkcs1())

    def generate_license(self, uid, app, days):
        expire_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

        payload = {
            "uid": uid,
            "app": app,
            "expire": expire_date
        }
        # 确保 JSON 格式一致
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))

        signature = rsa.sign(payload_json.encode('utf-8'), self.privkey, 'SHA-256')

        license_data = {
            "msg": payload_json,
            "sign": base64.b64encode(signature).decode('utf-8')
        }

        return base64.b64encode(json.dumps(license_data).encode('utf-8')).decode('utf-8')


# --- 仅供管理员测试用 ---
if __name__ == "__main__":
    # 实例化
    admin = AdminKeyGenerator()
    from AIPoke.key.uid import UID
    # 打印公钥，你需要把这个公钥复制到 license_validator.py 里！
    uid = UID().get_uid()
    print(uid)
    print("\n请将下方公钥复制到 license_validator.py 中:\n")
    print(admin.pubkey.save_pkcs1().decode())
    print("-" * 50)

    # 测试生成一个 Key
    target_hwid = input("输入目标机器码: ")
    key = admin.generate_license(target_hwid, 8, 60)
    print(key)
    key =admin.generate_license(target_hwid, 1, 30)
    print(key)
    print("-" * 50)