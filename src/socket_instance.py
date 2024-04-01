# socketio_instance.py
from flask_socketio import SocketIO
from src.logger import Logger
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

logger = Logger()


def emit_agent(channel, content):
    try:
        socketio.emit(channel, content)
        logger.info(f"SOCKET {channel} MESSAGE: {content}")
    except Exception as e:
        logger.error(f"SOCKET {channel} ERROR: {str(e)}")
