import logging


class DebugToWarningLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('INFO', 'DEBUG', 'WARNING')


class ErrorOrCriticalLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('ERROR', 'CRITICAL')
