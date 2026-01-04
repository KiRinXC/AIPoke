import hashlib
import wmi
import logging
import uuid

class UID:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_uuid(self, c):
        try:
            for item in c.Win32_ComputerSystemProduct():
                return item.UUID
        except Exception as e:
            self.logger.debug(f"Failed to get UUID: {e}")
        return None

    def _get_cpu_id(self, c):
        try:
            for cpu in c.Win32_Processor():
                return cpu.ProcessorId.strip()
        except Exception as e:
            self.logger.debug(f"Failed to get CPU ID: {e}")
        return None

    def _get_baseboard_serial(self, c):
        try:
            for board in c.Win32_BaseBoard():
                return board.SerialNumber
        except Exception as e:
            self.logger.debug(f"Failed to get baseboard serial: {e}")
        return None

    def _get_disk_serial(self, c):
        try:
            for disk in c.Win32_PhysicalMedia():
                return disk.SerialNumber.strip()
        except Exception as e:
            self.logger.debug(f"Failed to get disk serial: {e}")
        return None

    def _get_mac_address(self):
        mac = uuid.getnode()
        if mac:
            return ':'.join(['{:02x}'.format((mac >> i) & 0xff) for i in range(0, 48, 8)])
        return None

    def get_uid(self):
        try:
            c = wmi.WMI()
            components = []

            # 优先级从高到低
            components.append(self._get_uuid(c))
            components.append(self._get_cpu_id(c))
            components.append(self._get_baseboard_serial(c))
            components.append(self._get_disk_serial(c))
            components.append(self._get_mac_address())

            # 过滤掉 None 和无效值
            valid_components = [s for s in components if s and s.strip() and s.lower() not in ["none", "to be filled by o.e.m.", "000000000000"]]
            if not valid_components:
                self.logger.error("无法获取任何有效的硬件标识")
                return None

            # 拼接并哈希
            raw_id = "".join(valid_components).encode('utf-8')
            machine_hash = hashlib.sha256(raw_id).hexdigest()
            return machine_hash

        except Exception as e:
            self.logger.error(f"生成机器码时发生错误: {e}", exc_info=True)
            return None
