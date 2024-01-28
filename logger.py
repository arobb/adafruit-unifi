import logging
import syslog

class Logger(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.syslog = syslog.syslog

        self.logger.setLevel(logging.INFO)

    def debug(self, message):
        self.logger.debug(message)
        self.syslog(syslog.LOG_DEBUG, message)

    def info(self, message):
        self.logger.info(message)
        self.syslog(syslog.LOG_INFO, message)

    def warning(self, message):
        self.logger.warning(message)
        self.syslog(syslog.LOG_WARNING, message)

    def error(self, message):
        self.logger.error(message)
        self.syslog(syslog.LOG_ERR, message)