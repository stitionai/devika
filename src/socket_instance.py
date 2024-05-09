# socketio_instance.py
from flask_socketio import SocketIO
from src.logger import Logger


class EmitAgent:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_instances()
        return cls._instance

    def _initialize_instances(self):
        self.socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")
        self.logger = Logger()

    def get_socketio(self):
        return self.socketio

    def emit_content(self, channel, content, log=True):
        try:
            self.socketio.emit(channel, content)
            if log:
                self.logger.info(f"SOCKET {channel} MESSAGE: {content}")
            return True
        except Exception as e:
            self.logger.error(f"SOCKET {channel} ERROR: {str(e)}")
            return False
