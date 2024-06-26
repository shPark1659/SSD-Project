import os
from unittest import TestCase
from unittest.mock import Mock

from SSD.command import WriteCommand, EraseCommand
from SSD.ssd import SSDDriverCommon

if os.path.dirname(__file__) == '':
    CURRENT_DIR = os.getcwd()
else:
    CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
NAND_PATH = os.path.join(ROOT_DIR, 'nand.txt')
RESULT_PATH = os.path.join(ROOT_DIR, 'result.txt')


class TestCommand(TestCase):
    def setUp(self):
        self.ssd_driver = SSDDriverCommon('\n', NAND_PATH, RESULT_PATH)
        self.write_command = WriteCommand(self.ssd_driver, 1, "0x00000001")

    @staticmethod
    def clear_test_files(nand_path: str, result_path: str):
        if os.path.exists(nand_path):
            os.remove(nand_path)
        if os.path.exists(result_path):
            os.remove(result_path)
        pass

    def tearDown(self):
        self.clear_test_files(NAND_PATH, RESULT_PATH)

    def read_nand_file(self):
        with open(NAND_PATH, "r") as f:
            result_value = f.read().split(f"{self.ssd_driver.sep}")[1]
        return result_value

    @staticmethod
    def read_result_file():
        with open(RESULT_PATH, "r") as f:
            result_value = f.read()
        return result_value

    def test_execute_write_success(self):
        self.write_command.execute()
        self.assertEqual(int(self.read_nand_file()), 1)

    def test_execute_write_read_success(self):
        self.write_command.execute()
        self.ssd_driver.read(1)
        self.assertEqual(self.read_result_file(), "0x00000001")

    def test_execute_erase_success(self):
        self.ssd_driver = Mock()
        erase_command = EraseCommand(self.ssd_driver, 1, 1)
        erase_command.execute()
        self.ssd_driver.erase.assert_called_once()

    @staticmethod
    def erase(address: int, value: int):
        if value > 10:
            raise Exception
        return

    def test_erase_over_ten(self):
        self.ssd_driver = Mock()
        self.ssd_driver.erase.side_effect = self.erase
        erase_command = EraseCommand(self.ssd_driver, 1, 20)
        with self.assertRaises(Exception):
            erase_command.execute()
            self.fail()
        self.assertEqual(self.ssd_driver.erase.call_count, 2)
