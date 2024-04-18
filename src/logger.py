from functools import wraps

from fastlogging import LogInit
from flask import request

from src.config import Config


class Logger:
    _loggers = {}
    logger = None

    def __new__(cls, filename="devika_agent.log"):
        if filename not in cls._loggers:
            cls._loggers[filename] = super(Logger, cls).__new__(cls)
            cls._loggers[filename].logger = LogInit(pathName=Config().get_logs_dir() + "/" + filename, console=True, colors=True, encoding="utf-8")
            
        return cls._loggers[filename]

    def read_log_file(self) -> str:
        with open(self.logger.pathName, "r") as file:
            return file.read()

    def info(self, message: str):
        self.logger.info(message)
        self.logger.flush()

    def error(self, message: str):
        self.logger.error(message)
        self.logger.flush()

    def warning(self, message: str):
        self.logger.warning(message)
        self.logger.flush()

    def debug(self, message: str):
        self.logger.debug(message)
        self.logger.flush()

    def exception(self, message: str):
        self.logger.exception(message)
        self.logger.flush()


def route_logger(func):
    log_enabled = Config().get_logging_rest_api()
    logger = Logger()

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log entry point
        if log_enabled:
            logger.info(f"{request.path} {request.method}")

        # Call the actual route function
        response = func(*args, **kwargs)

        # Log exit point, including response summary if possible
        try:
            if log_enabled:
              if isinstance(response, Response) and response.direct_passthrough:
                  logger.debug(f"{request.path} {request.method} - Response: File response")
              else:
                  response_summary = response.get_data(as_text=True)
                  if 'settings' in request.path:
                      response_summary = "*** Settings are not logged ***"
                  logger.debug(f"{request.path} {request.method} - Response: {response_summary}")
        except Exception as e:
            logger.exception(f"{request.path} {request.method} - {e})")

        return response
    return wrapper
  