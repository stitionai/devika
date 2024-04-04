# socketio_instance.py
from flask_socketio import SocketIO
from src.logger import Logger
socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")

logger = Logger()


def emit_agent(channel, content, log=True):
    try:
        socketio.emit(channel, content)
        if log:
            logger.info(f"SOCKET {channel} MESSAGE: {content}")
        return True
    except Exception as e:
        logger.error(f"SOCKET {channel} ERROR: {str(e)}")
        return False
