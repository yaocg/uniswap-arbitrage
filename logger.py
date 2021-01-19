import logging
import sys
from logging import handlers

class Logger:
    """向文件及终端打印日志类
    """

    def __init__(self, filename, format_str="%(asctime)s - %(levelname)s - %(message)s"):
        formatter = logging.Formatter(format_str)

        fh = handlers.RotatingFileHandler(filename, mode="a", maxBytes=100000000, backupCount=3, encoding="UTF8")
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.INFO)

        self.logger_ = logging.getLogger()
        self.logger_.setLevel(logging.INFO)
        self.logger_.addHandler(ch)
        self.logger_.addHandler(fh)

    def setAppLevel(self, app, levelStr="error"):
        """设置某些类库的日志级别:
            参数:类库名称,日志级别
            返回:无
        """

        level = logging.ERROR
        if levelStr.lower() == "debug":
            level = logging.DEBUG
        elif levelStr.lower() == "info":
            level = logging.INFO
        elif levelStr.lower() == "warning":
            level = logging.WARNING
        elif levelStr.lower() == "error":
            level = logging.ERROR
        elif levelStr.lower() == "critical":
            level = logging.CRITICAL

        logging.getLogger(app).setLevel(level)

    def log(self, log_type, message, file_depth=3, line_depth=2):
        if log_type.lower() == "debug":
            self.debug(message, file_depth, line_depth)
        elif log_type.lower() == "info":
            self.info(message, file_depth, line_depth)
        elif log_type.lower() == "warning":
            self.warning(message, file_depth, line_depth)
        elif log_type.lower() == "error":
            self.error(message, file_depth, line_depth)
        elif log_type.lower() == "critical":
            self.critical(message, file_depth, line_depth)
        else:
            self.warning(message, file_depth, line_depth)

    def debug(self, message, file_depth=2, line_depth=1):
        """打印debug级别日志
            参数:信息
            返回:无
        """
        self.logger_.debug(self.__format(message, file_depth, line_depth))

    def info(self, message, file_depth=2, line_depth=1):
        """打印info级别日志
            参数:信息
            返回:无
        """
        self.logger_.info(self.__format(message, file_depth, line_depth))

    def warning(self, message, file_depth=2, line_depth=1):
        """打印warning级别日志
            参数:信息
            返回:无
        """
        self.logger_.warning(self.__format(message, file_depth, line_depth))

    def error(self, message, file_depth=2, line_depth=1):
        """打印error级别日志
            参数:信息
            返回:无
        """
        self.logger_.error(self.__format(message, file_depth, line_depth))

    def critical(self, message, file_depth=2, line_depth=1):
        """打印critical级别日志
            参数:信息
            返回:无
        """
        self.logger_.critical(self.__format(message, file_depth, line_depth))

    def __format(self, message, file_depth=2, line_depth=1):
        filename = sys._getframe(file_depth).f_code.co_filename
        lineno = sys._getframe(line_depth).f_back.f_lineno

        pos = filename.rfind("/")
        if pos != -1:
            filename = filename[pos+1:]
        return "{0}({1}): {2}".format(filename, lineno, message)
