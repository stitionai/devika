# create wrapper function that will has retry logic of 5 times
import sys
import time
from src.socket_instance import emit_agent

def retry_wrapper(func):
    def wrapper(*args, **kwargs):
        max_tries = 5
        tries = 0
        while tries < max_tries:
            result = func(*args, **kwargs)
            if result:
                return result
            print("Invalid response from the model, I'm trying again...")
            emit_agent("info", {"type": "warning", "message": "Invalid response from the model, trying again..."})
            tries += 1
            time.sleep(2)
        print("Maximum 5 attempts reached. try other models")
        emit_agent("info", {"type": "error", "message": "Maximum attempts reached. model keeps failing."})
        sys.exit(1)

        return False
    return wrapper
