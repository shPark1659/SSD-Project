import os.path

from LOGGER.logger import Logger


class Command:
    def __init__(self, driver, address, val):
        self.driver = driver
        self.val = val
        self.address = address

    def execute(self):
        pass

    def get_value(self):
        return self.val


class WriteCommand(Command):
    def __init__(self, driver, address, val):
        super().__init__(driver, address, val)
        self.type = "W"


class EraseCommand(Command):
    def __init__(self, driver, address, val):
        super().__init__(driver, address, val)
        self.type = "E"


CMD_WRITE = "W"
CMD_ERASE = "E"


class SSDBuffer:
    def __init__(self, driver):
        self.db_path = "../buffer.txt"
        self.logger = Logger()
        self.driver = driver
        self.commands = self.load_db()
        self.cnt = 0

    def update(self, command_type, address, value=None):
        if command_type == "R":
            self.read(address)
            return
        elif command_type == "F":
            self.flush()
            return

        command = self.create_command(command_type, address, value)
        self.commands[address] = command
        self.optimize()
        if self.need_buffer_flush():
            self.flush()
        self.save_db()
        self.cnt += 1

    def read(self, address):
        ret = self.find(address)
        if ret is None:
            self.driver.read(address)
        else:
            with open(self.driver.result_path, 'w') as file:
                file.write(ret)

    def create_command(self, command_type, address, value):
        if command_type == CMD_WRITE:
            return WriteCommand(self.driver, address, value)
        elif command_type == CMD_ERASE:
            return EraseCommand(self.driver, address, value)
        self.logger.log(f"invalid command type {command_type}")

    def save_db(self):
        data = self.make_db()
        with open(self.db_path, "w") as f:
            f.write(data)

    def load_db(self):
        if not os.path.exists(self.db_path):
            return {}

        ret = {}
        with open(self.db_path, "r") as f:
            self.cnt = f.readline()
            for line in f:
                args = line.strip().split(" ")
                ret[int(args[1])] = self.create_command(args[0], int(args[1]), int(args[2]))
        return ret

    def find(self, address):
        if address in self.commands:
            return '0x' + f'{self.commands[address].get_value():08x}'.upper()
        return None

    def optimize(self):
        pass

    def need_buffer_flush(self):
        return self.cnt >= 10

    def flush(self):
        for command in self.commands:
            command.execute()

        self.commands.clear()
        self.save_db()

    def make_db(self):
        return f"{self.cnt}\n" + "\n".join([f"{x.type} {x.address} {x.val}" for x in self.commands.values()])
