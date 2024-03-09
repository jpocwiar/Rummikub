from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QColor
from logging.handlers import RotatingFileHandler
import logging
import os

class Logger(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_handler = RotatingFileHandler("logfile.log", maxBytes=10000, backupCount=1)
        self.file_handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(self.formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        self.setReadOnly(True)
        self.clear()
        if os.path.exists("logfile.log"):
            with open("logfile.log", "w"):
                pass

    def log(self, message):
        self.logger.info(message)

        self.setTextColor(QColor('black'))
        self.append(message)
        print(message)

    def error(self, message):
        self.logger.warning(f'[BŁĄD] {message}\n')

        self.setTextColor(QColor('red'))
        self.append(f'[BŁĄD] {message}')
        print("\033[91m[BŁĄD] {}\033[0m".format(message))
