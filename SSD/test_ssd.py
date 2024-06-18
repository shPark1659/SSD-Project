from unittest import TestCase
from unittest.mock import Mock, patch

from ssd_main import SSDApplication
from ssd import SSDDriverComma, SSDDriver
import os


class TestSSDDriver(TestCase):
    def test_init_SSDDriverComma(self):
        nand_path = 'nand_temp.txt'
        result_path = 'result_temp.txt'
        ssd = SSDDriverComma(nand_path, result_path)
        self.assertTrue(os.path.isfile(nand_path))
        self.clear_files(nand_path, result_path)

    def test_write_SSDDriverComma(self):
        nand_path = 'nand_temp.txt'
        result_path = 'result_temp.txt'
        ssd = SSDDriverComma(nand_path, result_path)
        ssd.write()
        self.assertTrue(os.path.isfile(nand_path))
        self.clear_files(nand_path, result_path)

    def clear_files(self, nand_path, result_path):
        if os.path.exists(nand_path):
            os.remove(nand_path)
        if os.path.exists(result_path):
            os.remove(result_path)


class TestSSDMain(TestCase):
    def test_main_invalid_input_read(self):
        app = SSDApplication()
        ret = app.main(["R", "-1"])
        self.assertEqual(ret, False)
        ret = app.main(["R", "100"])
        self.assertEqual(ret, False)

    @patch.object(SSDApplication, "create_ssd_driver")
    def test_main_read(self, mk_driver_factory):
        mk = Mock(spec=SSDDriver)
        mk.read.side_effect = "driver : read"
        mk.write.side_effect = "driver : write"
        mk_driver_factory.return_value = mk
        app = SSDApplication()
        ret = app.main(["R", "0"])
        self.assertEqual(ret, True)
        self.assertEqual(mk.read.call_count, 1)

    def test_main_invalid_input_write(self):
        app = SSDApplication()
        ret = app.main(["W", "-1", "0x00000000"])
        self.assertEqual(ret, False)
        ret = app.main(["W", "100", "0x00000000"])
        self.assertEqual(ret, False)
        ret = app.main(["W", "0", "1"])
        self.assertEqual(ret, False)
        ret = app.main(["W", "0", "0xFF"])
        self.assertEqual(ret, False)
        ret = app.main(["W", "0", "0x123456789"])
        self.assertEqual(ret, False)

    @patch.object(SSDApplication, "create_ssd_driver")
    def test_main_write(self, mk_driver_factory):
        mk = Mock(spec=SSDDriver)
        mk.read.side_effect = "driver : read"
        mk.write.side_effect = "driver : write"
        mk_driver_factory.return_value = mk
        app = SSDApplication()
        ret = app.main(["W", "0", "0x12345678"])
        self.assertEqual(ret, True)
        self.assertEqual(mk.write.call_count, 1)
