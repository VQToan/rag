import logging

from src.utils.logger.error_handler import NotiErrorHandler


class Logger:
    def __init__(self):
        self.logger = logging.getLogger('waitress')
        self.logger.setLevel(logging.INFO)
        noti_error_handler = NotiErrorHandler()
        noti_error_handler.setLevel(logging.ERROR)
        self.logger.addHandler(noti_error_handler)

    def __call__(self, *args, **kwargs):
        return self.logger