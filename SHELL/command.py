import os, sys
from abc import ABC, abstractmethod

if os.path.dirname(__file__) == '':
    CURRENT_DIR = os.getcwd()
else:
    CURRENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CURRENT_DIR)
RESULT_PATH = os.path.join(ROOT_DIR, 'result.txt')
MAX_ADDRESS = 100

sys.path.append(ROOT_DIR)
from SHELL.ssd_handler import SSDHandler
from LOGGER.logger import Logger


class Command(ABC):
    def __init__(self):
        self.ssd = SSDHandler()
        self.logger = Logger()
        self.logger.log('Complete initialization')

    def execute(self, *args):
        if not self.check_valid(*args):
            print('INVALID COMMAND')
            self.logger.log('Invalid command')
            return
        self.run(*args)

    @abstractmethod
    def run(self, *args):
        pass

    @abstractmethod
    def check_valid(self, *args):
        pass

    @staticmethod
    def print_pass(is_pass: bool):
        if is_pass:
            print("Pass")
        else:
            print("Fail")

    @staticmethod
    def is_address_valid(address: str):
        if not address.isdigit():
            return False
        if not 0 <= int(address) <= 99:
            return False
        return True

    @staticmethod
    def is_data_valid(data: str):
        if len(data) != 10:
            return False
        if not data.startswith("0x"):
            return False
        try:
            int(data, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_size(start: str, size: str):
        if not size.isdigit():
            return False
        if int(size) <= 0:
            return False
        if int(start) + int(size) > MAX_ADDRESS:
            return False
        return True


class WriteCommand(Command):
    def __init__(self):
        super().__init__()

    def check_valid(self, *args):
        if len(args) != 2:
            self.logger.log('Invalid argument length')
            return False
        if not self.is_address_valid(args[0]):
            self.logger.log('Invalid address')
            return False
        if not self.is_data_valid(args[1]):
            self.logger.log('Invalid data format')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        self.ssd.write(*args)
        self.logger.log('Complete write ssd')


class ReadCommand(Command):
    def check_valid(self, *args):
        if len(args) != 1:
            self.logger.log('Invalid argument length')
            return False
        if not self.is_address_valid(args[0]):
            self.logger.log('Invalid address')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        ret = self.ssd.read(*args)
        self.logger.log('Complete read ssd')
        if ret == 0:
            with open(RESULT_PATH, 'r') as fp:
                print(fp.readline().strip())
                self.logger.log('Read result file')


class FullWriteCommand(Command):
    def check_valid(self, *args):
        if len(args) != 1:
            self.logger.log('Invalid argument length')
            return False
        if not self.is_data_valid(args[0]):
            self.logger.log('Invalid data format')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        for address in range(MAX_ADDRESS):
            self.ssd.write(str(address), args[0])
        self.logger.log('Complete fullwrite ssd')


class FullReadCommand(Command):
    def check_valid(self, *args):
        if len(args) != 0:
            self.logger.log('Invalid argument length')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        for address in range(MAX_ADDRESS):
            self.ssd.read(str(address))
            with open(RESULT_PATH, 'r') as fp:
                print(fp.readline().strip())
        self.logger.log('Complete fullread ssd')


class HelpCommand(Command):
    def check_valid(self, *args):
        if len(args) != 0:
            self.logger.log('Invalid argument length')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        print(
            '----------- HOW TO TEST SSD -----------',
            '------(Enter command on the right)------',
            'To WRITE new data : write {LBA index} {data}',
            'To READ written data : read {LBA index}',
            'To WRITE data on all LBA : fullwrite {data}',
            'To READ every data from 0~99 LBA : fullread',
            'To ERASE data for certain size : erase {start LBA} {# of LBA}',
            'To ERASE data from start to end LBA : erase_range {start LBA} {end LBA}',
            'To test pre-defined scenario : run_list.txt',
            'To finish this app : exit',
            'To repeat this information : help',
            sep='\n')
        self.logger.log('Print help script')


class TestApp1Command(Command):
    def __init__(self):
        super().__init__()
        self.write_value = '0xABCDFFFF'

    def check_valid(self, *args):
        if len(args) != 0:
            self.logger.log('Invalid argument length')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        is_pass = True

        # Fullwrite
        for address in range(MAX_ADDRESS):
            self.ssd.write(str(address), self.write_value)
        self.logger.log('Complete fullwrite')

        # Fullread
        for address in range(MAX_ADDRESS):
            self.ssd.read(str(address))
            with open(RESULT_PATH, 'r') as fp:
                read_value = fp.readline().strip()
            print(read_value)
            is_pass &= self.write_value == read_value
        self.logger.log('Complete fullread')
        self.print_pass(is_pass)


class TestApp2command(Command):
    def __init__(self):
        super().__init__()
        self.write_1st_value = '0xAAAABBBB'
        self.write_2nd_value = '0x12345678'

    def check_valid(self, *args):
        if len(args) != 0:
            self.logger.log('Invalid argument length')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        is_pass = True

        # write LBA[0:6] * 30
        for i in range(30):
            for addr in range(6):
                self.ssd.write(str(addr), self.write_1st_value)
        self.logger.log('Complete write 30times')
        # write LBA[0:6]
        for addr in range(6):
            self.ssd.write(str(addr), self.write_2nd_value)
        self.logger.log('Complete re-write')
        # read LBA[0:6]
        for addr in range(6):
            self.ssd.read(str(addr))
            with open(RESULT_PATH, 'r') as fp:
                value = fp.readline().strip()
            print(value)
            is_pass &= self.write_2nd_value == value
        self.logger.log('Complete read')
        self.print_pass(is_pass)


class EraseCommand(Command):
    def check_valid(self, *args):
        if len(args) != 2:
            self.logger.log('Invalid argument length')
            return False
        if not self.is_address_valid(args[0]):
            self.logger.log('Invalid address')
            return False
        if not self.is_valid_size(*args):
            self.logger.log('Invalid erase size')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        steps = self.get_steps_with_size(int(args[0]), int(args[1]))
        for n in range(len(steps) - 1):
            size = steps[n + 1] - steps[n]
            self.ssd.erase(steps[n], size)
        self.logger.log('Complete erase')


    @staticmethod
    def get_steps_with_size(start, size):
        end = start + size
        numbers = list(range(start, end, 10))
        if numbers and numbers[-1] != end:
            numbers.append(end)
        elif not numbers:
            numbers.append(end)

        return numbers


class EraseRangeCommand(Command):
    def check_valid(self, *args):
        if len(args) != 2:
            self.logger.log('Invalid argument length')
            return False
        if not self.is_address_valid(args[0]):
            self.logger.log('Invalid address')
            return False
        if not self.is_address_valid(str(int(args[1]) - 1)):
            self.logger.log('Invalid address')
            return False
        if int(args[0]) >= int(args[1]):
            self.logger.log('Invalid address')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        steps = self.get_steps_with_end(int(args[0]), int(args[1]))
        for n in range(len(steps) - 1):
            size = steps[n + 1] - steps[n]
            self.ssd.erase(steps[n], size)
        self.logger.log('Complete erase_range')

    @staticmethod
    def get_steps_with_end(start, end):
        numbers = list(range(start, end, 10))
        if numbers and numbers[-1] != end:
            numbers.append(end)
        elif not numbers:
            numbers.append(end)

        return numbers

class FlushCommand(Command):
    def check_valid(self, *args):
        if len(args) != 0:
            self.logger.log('Invalid argument length')
            return False
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        self.ssd.flush()
        self.logger.log('Complete flush')


class ExitCommand(Command):
    def check_valid(self, *args):
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        self.logger.log('Exit')
        exit(0)


class InvalidCommand(Command):
    def check_valid(self, *args):
        self.logger.log('Valid argument')
        return True

    def run(self, *args):
        print("INVALID COMMAND")
        self.logger.log('Invalid command')
