# create wrapper function that will has retry logic of 5 times
import sys
import time
from functools import wraps
import json

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

        
class InvalidResponseError(Exception):
    pass

def validate_responses(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = list(args)
        response = args[1]
        response = response.strip()

        try:
            response = json.loads(response)
            print("first", type(response))
            args[1] = response
            return func(*args, **kwargs)

        except json.JSONDecodeError:
            pass

        try:
            response = response.split("```")[1]
            if response:
                response = json.loads(response.strip())
                print("second", type(response))
                args[1] = response
                return func(*args, **kwargs)

        except (IndexError, json.JSONDecodeError):
            pass

        try:
            start_index = response.find('{')
            end_index = response.rfind('}')
            if start_index != -1 and end_index != -1:
                json_str = response[start_index:end_index+1]
                try:
                    response = json.loads(json_str)
                    print("third", type(response))
                    args[1] = response
                    return func(*args, **kwargs)

                except json.JSONDecodeError:
                    pass
        except json.JSONDecodeError:
            pass

        for line in response.splitlines():
            try:
                response = json.loads(line)
                print("fourth", type(response))
                args[1] = response
                return func(*args, **kwargs)

            except json.JSONDecodeError:
                pass

        # If all else fails, raise an exception
        emit_agent("info", {"type": "error", "message": "Failed to parse response as JSON"})
        # raise InvalidResponseError("Failed to parse response as JSON")
        return False

    return wrapper