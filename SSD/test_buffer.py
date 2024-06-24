import os
from unittest import TestCase

from SSD.buffer import SSDBuffer
from SSD.ssd import SSDDriverEnter

if os.path.dirname(__file__) == '':
    CURRENT_DIR = os.getcwd()
else:
    CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
BUFFER_PATH = os.path.join(ROOT_DIR, "buffer.txt")
NAND_PATH = os.path.join(ROOT_DIR, 'nand.txt')
RESULT_PATH = os.path.join(ROOT_DIR, 'result.txt')


class TestSSDBuffer(TestCase):
    def setUp(self):
        self.buffer = SSDBuffer(SSDDriverEnter(NAND_PATH, RESULT_PATH))

    def tearDown(self):
        self.clear_test_files()

    def test_write_after_read(self):
        self.buffer.update("W", 1, "0x00000002")

        self.buffer.read(1)
        result = self.get_value(RESULT_PATH)
        self.assertEqual(result, "0x00000002")

    def test_read_first(self):
        self.buffer.read(1)
        result = self.get_value(RESULT_PATH)
        self.assertEqual(result, "0x00000000")

    def test_write_after_erase(self):
        self.buffer.update("W", 1, "0x00000002")
        self.buffer.update("E", 1, "0x00000002")
        self.buffer.read(1)
        result = self.get_value(RESULT_PATH)
        self.assertEqual(result, "0x00000000")

    def test_invalid_command_type(self):
        self.buffer.update("D", 1, 2)

    def test_save_db(self):
        self.buffer.update("W", 1, "0x00000002")
        self.buffer.update("W", 2, "0x00000003")
        with open(BUFFER_PATH, "r") as f:
            result = f.read()
        self.assertEqual(result, '2' + '\n' + 'W 1 0x00000002' + '\n' + 'W 2 0x00000003' + '\n')

    def test_load_db(self):
        with open(BUFFER_PATH, "w") as f:
            f.write("1\nW 1 0x00000002")

        self.assertEqual(len(self.buffer.load_db()), 1)

    def test_optimize_ignore_write_1(self):
        self.buffer.update("W", 20, "0xABCDABCD")
        self.buffer.update("W", 21, "0x12341234")
        self.buffer.update("W", 20, "0xEEEEFFFF")
        self.assertEqual(len(self.buffer.commands), 2)
        self.assertEqual(self.buffer.read(20), "0xEEEEFFFF")

    def test_optimize_ignore_write_2(self):
        self.buffer.update("W", 20, "0xABCDABCD")
        self.buffer.update("W", 21, "0x12341234")
        self.buffer.update("E", 18, "5")
        self.assertEqual(len(self.buffer.commands), 1)
        self.assertEqual(self.buffer.read(20), "0x00000000")
        self.assertEqual(self.buffer.read(21), "0x00000000")

    def test_optimize_ignore_write_3(self):
        self.buffer.update("W", 20, "0xABCDABCD")
        self.buffer.update("E", 10, "2")
        self.buffer.update("E", 12, "3")

        self.assertEqual(len(self.buffer.commands), 2)
        self.assertEqual(self.buffer.read(20), "0xABCDABCD")

    def test_optimize_ignore_write_4_1(self):
        self.buffer.update("E", 10, "4")
        self.buffer.update("E", 40, "5")
        self.buffer.update("W", 12, "0xABCD1234")
        self.buffer.update("W", 13, "0x4BCD5351")

        self.assertEqual(len(self.buffer.commands), 4)
        self.assertEqual(self.buffer.read(12), "0xABCD1234")
        self.assertEqual(self.buffer.read(13), "0x4BCD5351")

    def test_optimize_ignore_write_4_2(self):
        self.buffer.update("E", 50, "1")
        self.buffer.update("E", 40, "5")
        self.buffer.update("W", 50, "0xABCD1234")

        self.assertEqual(len(self.buffer.commands), 2)
        self.assertEqual(self.buffer.read(50), "0xABCD1234")

    def test_optimize_ignore_write_5(self):
        self.buffer.update("E", 10, "2")
        self.buffer.update("W", 10, "ABCDABCD")
        self.buffer.update("E", 12, "3")
        self.assertEqual(len(self.buffer.commands), 2)
        self.assertEqual(self.buffer.read(10), "0xABCDABCD")

    def test_flush(self):
        self.buffer.update("W", 1, "0x00000005")
        self.buffer.update("W", 0, "0x00000005")
        self.buffer.update("W", 6, "0x00000005")
        self.assertNotEqual(self.read(1), "0x00000005")
        self.buffer.flush()
        self.assertEqual(self.read(1), "0x00000005")

    def read(self, address):
        self.buffer.driver.read(1)
        return self.get_value(RESULT_PATH)

    @staticmethod
    def get_value(path: str) -> str:
        with open(path, 'r') as file:
            data = file.readline().strip()
        return data

    @staticmethod
    def clear_test_files():
        if os.path.exists(NAND_PATH):
            os.remove(NAND_PATH)
        if os.path.exists(RESULT_PATH):
            os.remove(RESULT_PATH)
        if os.path.exists(BUFFER_PATH):
            os.remove(BUFFER_PATH)
        pass
