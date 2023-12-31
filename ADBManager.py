from adbutils import adb, errors
from PyQt6 import QtCore


class ADBManager(QtCore.QThread):

    adb_address = ""

    def connect(self, address: str):
        self.adb_address = address
        try:
            QtCore.QThread.sleep(1)
            adb.connect(self.adb_address, timeout=10)
            device = adb.device(serial=self.adb_address)
            QtCore.QThread.sleep(1)
            return device

        except errors.AdbError as e:
            raise e
        except Exception as e:
            raise e
