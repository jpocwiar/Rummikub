from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import logging
from logging.handlers import RotatingFileHandler
import os

class Logger:
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self.file_handler = RotatingFileHandler("logfile.log", maxBytes=10000, backupCount=1)
        self.file_handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(self.formatter)
        self.logger = logging.getLogger()
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        #self.clear()
        if os.path.exists("logfile.log"):
            with open("logfile.log", "w"):
                pass

    def log(self, message):
        # Logowanie informacji do pliku dziennika zdarzeń
        self.logger.info(message)

        self.text_edit.setTextColor(QColor('black'))
        self.text_edit.append(message)

        # Aktualizacja widoku kontrolki QTextEdit
        # self.text_edit.setTextColor(QColor('black'))
        # self.text_edit.append(message)

    def error(self, message):

        self.logger.warning(f'[BŁĄD] {message}\n')

        # Aktualizacja widoku kontrolki QTextEdit
        self.text_edit.setTextColor(QColor('red'))
        self.text_edit.append(f'[BŁĄD] {message}')