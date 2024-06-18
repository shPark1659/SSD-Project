from abc import ABC, abstractmethod
import os

MAX_DATA_LENGTH = 20


class SSDDriver(ABC):
    def __init__(self, nand_path, result_path):
        if not os.path.isfile(nand_path):
            with open(nand_path, 'w') as file:
                pass
        self.nand_path = nand_path
        self.result_path = result_path

    @abstractmethod
    def read(self, addr):
        pass

    @abstractmethod
    def write(self, addr, value):
        pass


class SSDDriverEnter(SSDDriver):
    def __init__(self, nand_path, result_path):
        super().__init__(nand_path, result_path)

    @staticmethod
    def convert_decimal_to_hex(decimal: int):
        return '0x{:08x}'.format(decimal)

    def read(self, addr: int):
        nand_data = ''
        with open(self.nand_path, 'r') as nand_file:
            nand_data = int(nand_file.read().split('\n')[:MAX_DATA_LENGTH][addr])
        with open(self.result_path, 'w') as result_file:
            result_file.write(self.convert_decimal_to_hex(nand_data))

    def write(self, addr: int, value: str):
        if not os.path.exists(self.nand_path):
            initial_data = ""
            for i in range(20):
                initial_data += "0" + "\n"
            with open(self.nand_path, 'w') as nand_file:
                nand_file.write(initial_data)

        with open(self.nand_path, 'r') as nand_file:
            nand_full_data = list(map(int, nand_file.read().split('\n')[:MAX_DATA_LENGTH]))
        nand_full_data[addr] = int(value, 16)

        nand_new_data = ""
        for i in range(20):
            nand_new_data += str(nand_full_data[i]) + "\n"
        with open(self.nand_path, 'w') as nand_file:
            nand_file.write(nand_new_data)


class SSDDriverComma(SSDDriver):
    def __init__(self, nand_path, result_path):
        super().__init__(nand_path, result_path)

    def read(self):
        buffer = ''
        with open(self.nand_path, 'r') as nand:
            buffer = nand.readlines()

    def write(self):
        pass
