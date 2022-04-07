from __future__ import annotations
import threading
from copy import deepcopy
import os
from solar.presets import DATA_PATH
from logging import Formatter, LogRecord
import logging
from datetime import datetime
# [Code coming from Kivy Logger ALL RIGHT RESERVED]
# Sequences to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

BLACK, RED, GREEN, YELLOW, BLUE, _, CYAN, WHITE = list(range(8))

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': CYAN,
    'CRITICAL': RED,
    'ERROR': RED}

# This code is mostly inspired by kivy logger lib ALL RIGHT RESERVED
# Kivy logger is not directly used to avoid dependencies


class ColoredFormatter(Formatter):
    """Formatter adding color codes for levelnames. 
    It also changes the behaviour for logging sources:
    "App: Message" will be streamed [LEVEL ] [App ] Message. 
    Note that the ':' are required to get app inside brackets.
    """

    def __init__(self, colored: bool = True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.colored = colored

    def format(self, record: LogRecord) -> str:
        """Formats record arg accordingly to self's spec.

        Args:
        -----
            record (LogRecord): The modified record

        Returns:
        --------
            str: the formatted message => [LEVEL ] [App ] Message

        See: 
        ----
            ``super().format()``
        """
        record = deepcopy(record)
        splitted_message = record.msg.split(':', 1)
        if len(splitted_message) >= 2:
            # Re-format
            record.msg = '[%-12s]%s' % (splitted_message[0],
                                        splitted_message[1])
        levelname = record.levelname
        if self.colored and levelname in COLORS:
            col = COLORS[levelname]
            record.levelname = (
                COLOR_SEQ % (30 + col) + levelname + RESET_SEQ)
        return logging.Formatter.format(self, record)


class FileHandlerWLVLName(logging.FileHandler):
    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        self.stream.write('[%-7s]' % record.levelname)
        self.stream.write(msg + '\n')
        self.stream.flush()
        return


# Overriding other libs logging except the kivy one
if logging.root.name != "kivy":
    logging.basicConfig(level=logging.INFO)
    Logger = logging.getLogger().getChild("solar")
    Logger.propagate = False
    Logger.manager = logging.Manager(Logger)
    syslog = logging.StreamHandler()
    syslog.setFormatter(ColoredFormatter(
        fmt='[%(levelname)-18s] %(message)s'))

    logging.root = Logger
    if not logging.root.hasHandlers():
        Logger.addHandler(syslog)
else:
    Logger = logging.root
# Logging in file
_LOG_PATH = (DATA_PATH / "logs")
try:
    _LOG_PATH.mkdir()
except OSError:
    pass


os.chmod(_LOG_PATH, 777)
i = 0
pth = _LOG_PATH / f"solar_{datetime.now().date()}_{i}.log"
while os.path.exists(pth):
    i += 1
    pth = _LOG_PATH / f"solar_{datetime.now().date()}_{i}.log"

filelogs = FileHandlerWLVLName(pth, encoding="utf-8")
file_fmt = ColoredFormatter(colored=False)
filelogs.setFormatter(file_fmt)

_lock = threading.Lock()
_lock.acquire()
Logger.handlers.insert(0, filelogs)
_lock.release()
Logger.info(f"Solar LOG: Record log in {pth}")
