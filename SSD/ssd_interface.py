import sys
import os

from ssd import SSDDriverComma, SSDDriver, SSDDriverEnter, SSDDriverCommon

COMMA_TYPE = "comma"
ENTER_TYPE = "enter"
ARG_LEN = 3
if os.path.dirname(__file__) == '':
    CURRENT_DIR = os.getcwd()
else:
    CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)


class Argument:
    def __init__(self, operation, address, value=None):
        self.operation = operation
        self.address = address
        self.value = value

    def set_operation(self, op):
        self.operation = op

    def set_address(self, addr):
        self.address = addr

    def set_value(self, val):
        self.value = val


class SSDInterface:
    def __init__(self, nand_file="nand.txt", result_file="result.txt"):
        self.nand_path = os.path.join(ROOT_DIR, nand_file)
        self.result_path = os.path.join(ROOT_DIR, result_file)
        self.args = None

    def main(self, inputs: list) -> int:
        self.args = self.get_parsed_arg(inputs)
        self.check_arguments()
        driver = self.create_ssd_driver(COMMA_TYPE)
        if self.args.operation == 'R':
            driver.read(int(self.args.address))
        if self.args.operation == 'W':
            driver.write(int(self.args.address), self.args.value)
        if self.args.operation == 'E':
            driver.erase(int(self.args.address), int(self.args.value))

    @staticmethod
    def get_parsed_arg(args: list) -> Argument:
        if len(args) < ARG_LEN:
            args += [None] * (ARG_LEN - len(args))
        return Argument(args[0], args[1], args[2])

    def check_arguments(self):
        if self.args.operation == 'R':
            self.check_address()
        elif self.args.operation == 'W':
            self.check_address()
            self.check_value()
        elif self.args.operation == 'E':
            self.check_address()
            pass  # TODO; whether to check size
        else:
            self.error()

    def check_value(self):
        if len(self.args.value) != 10:
            self.error()
        if not self.args.value.startswith('0x'):
            self.error()
        try:
            int(self.args.value, 16)
        except Exception:
            self.error()

    def check_address(self):
        if not isinstance(self.args.address, str) or not self.args.address.isdigit():
            self.error()
        if not 0 <= int(self.args.address) <= 99:
            self.error()

    @staticmethod
    def error():
        print('Invalid Arguments!')
        sys.exit(1)

    def create_ssd_driver(self, driver_type: str) -> SSDDriver:
        return SSDDriverCommon(',', self.nand_path, self.result_path)


if __name__ == '__main__':
    app = SSDInterface()
    app.main(sys.argv[1:])
