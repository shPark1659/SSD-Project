from unittest import TestCase, skip

from unittest.mock import Mock

from SHELL.TestShellApplication import TestShellApplication


class TestTestShellApplication(TestCase):
    def setUp(self):
        super().setUp()
        self.mk_ssd = Mock()
        self.shell = TestShellApplication(self.mk_ssd)

    def test_verify_write_incorrect_address(self):
        self.assertEqual(False, self.shell.run("write 100 OxAAAABBBB"))
        self.assertEqual(False, self.shell.run("write -1 OxAAAABBBB"))
        self.assertEqual(False, self.shell.run("write 0x11 OxAAAABBBB"))

    def test_verify_write_incorrect_data(self):
        self.assertEqual(False, self.shell.run("write 3 OxAAAABBBB"))
        self.assertEqual(False, self.shell.run("write 3 0xAABBBB"))
        self.assertEqual(False, self.shell.run("write 3 0xAAAABBBBCC"))

    def test_verify_correct_write_command(self):
        self.assertEqual(False, self.shell.run("write 3 0xAAAABBBB"))

    def test_call_ssd_read_when_shell_read(self):
        self.mk_ssd.read.return_value = '1'
        shell = TestShellApplication(self.mk_ssd)
        shell.read(3)

        self.assertEqual(1, self.mk_ssd.read.call_count)

    def test_call_ssd_read_when_shell_fullread(self):
        self.mk_ssd.read.return_value = '1'
        shell = TestShellApplication(self.mk_ssd)
        shell.fullread()

        self.assertEqual(100, self.mk_ssd.read.call_count)

    def test_call_ssd_write_when_shell_write(self):
        self.mk_ssd.write.return_value = '1'
        shell = TestShellApplication(self.mk_ssd)
        shell.write(3, '0xAAAABBBB')

        self.assertEqual(1, self.mk_ssd.write.call_count)

    def test_call_ssd_write_100_when_shell_fullwrite(self):
        self.mk_ssd.write.return_value = '1'
        shell = TestShellApplication(self.mk_ssd)
        shell.fullwrite('0xAAAABBBB')

        self.assertEqual(100, self.mk_ssd.write.call_count)
