from client import ClientKeyManager
from admin import AdminKeyGenerator
from AIPoke.utili.log_manager import init_logging
if __name__ == '__main__':
    init_logging(is_debug=True)
    admin = AdminKeyGenerator()
    client = ClientKeyManager()
    uid = client.uid
    # print(uid)
    # fake_uid = uid.replace('1', '2')
    # print(fake_uid)
    # key_1 = admin.generate_license(uid=uid,app='1',days=10)
    # key_2 = admin.generate_license(uid=fake_uid,app=2,days=20)
    # key_3 = admin.generate_license(uid=uid,app='3',days=9999)
    # key_4 = admin.generate_license(uid=uid,app='4',days=-21)
    # key_5 = admin.generate_license(uid=uid,app='1',days=25)
    # key_6 = admin.generate_license(uid=uid,app='2',days=30)
    # print(key_1)
    # print(key_2)
    # print(key_3)
    # print(key_4)
    # print(key_5)
    # print(key_6)
    #
    # client.save_key(key_1)
    # client.save_key(key_2)
    # client.get_active_permissions()
    # client.save_key(key_3)
    # client.save_key(key_4)
    # client.get_active_permissions()
    # client.save_key(key_5)
    # client.save_key(key_6)
    # client.get_active_permissions()

    print(client.get_active_permissions())


