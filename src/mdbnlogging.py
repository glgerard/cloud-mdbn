import sys

INFO=20
DEBUG=10

class Logger():
    def __init__(self):
        self.hdlr = sys.stderr
        self.log_level = INFO

    def info(self, message):
        self.hdlr.write(message + '\n')
        self.hdlr.flush()

    def debug(self, message):
        if self.log_level == DEBUG:
            self.hdlr.write(message + '\n')
            self.hdlr.flush()

root = Logger()

def basicConfig(filename=None, log_level=INFO):
    if filename:
        root.hdlr = open(filename, 'w')
    else:
        root.hdlr = sys.stderr
    root.log_level=log_level

def info(message):
    root.info(message)

def debug(message):
    root.debug(message)
