# socketio_instance.py
from flask_socketio import SocketIO
from src.logger import Logger
socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")

logger = Logger()


def emit_agent(channel, content, log=True):
    """Emit a message to a specified channel using Socket.IO.
    
    This function sends a message to the specified channel and optionally logs the emission. If logging is enabled, it logs
    an informational message with the channel and content.
    
    Args:
        channel (str): The name of the channel to emit the message to.
        content (any): The content of the message to be emitted. This can be any data type
            that is serializable by Socket.IO.
        log (bool?): A flag indicating whether to log the emission. Defaults to True.
    
    Returns:
        bool: True if the message was successfully emitted, False otherwise.
    """
    try:
        socketio.emit(channel, content)
        if log:
            logger.info(f"SOCKET {channel} MESSAGE: {content}")
        return True
    except Exception as e:
        logger.error(f"SOCKET {channel} ERROR: {str(e)}")
        return False
