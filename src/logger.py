from fastlogging import LogInit

from src.config import Config

class Logger:
    def __init__(self):
        config = Config()
        logs_dir = config.get_logs_dir()
        self.logger = LogInit(pathName=logs_dir + "/devika_agent.log", console=True, colors=True)

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
