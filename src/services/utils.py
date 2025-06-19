# create wrapper function that will has retry logic of 5 times
import sys
import time
from functools import wraps
import json

from src.socket_instance import emit_agent

def retry_wrapper(func):
    def wrapper(*args, **kwargs):
        max_tries = 3  # Reduced from 5 to 3 for faster failure
        tries = 0
        while tries < max_tries:
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
                print(f"Invalid response from the model, attempt {tries + 1}/{max_tries}")
                emit_agent("info", {"type": "warning", "message": f"Invalid response from the model, trying again... (attempt {tries + 1}/{max_tries})"})
            except Exception as e:
                print(f"Error in attempt {tries + 1}: {str(e)}")
                emit_agent("info", {"type": "error", "message": f"Error in attempt {tries + 1}: {str(e)}"})
                
            tries += 1
            if tries < max_tries:
                time.sleep(2)
                
        print(f"Maximum {max_tries} attempts reached. Operation failed.")
        emit_agent("info", {"type": "error", "message": f"Maximum {max_tries} attempts reached. Operation failed."})
        return False
    return wrapper

        
class InvalidResponseError(Exception):
    pass

def validate_responses(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            args = list(args)
            response = args[1]
            
            if not response:
                return False
                
            response = response.strip()

            # Try to parse as JSON directly
            try:
                response_json = json.loads(response)
                args[1] = response_json
                return func(*args, **kwargs)
            except json.JSONDecodeError:
                pass

            # Try to extract JSON from code blocks
            try:
                if "```json" in response:
                    start = response.find("```json") + 7
                    end = response.find("```", start)
                    if end != -1:
                        json_str = response[start:end].strip()
                        response_json = json.loads(json_str)
                        args[1] = response_json
                        return func(*args, **kwargs)
                elif "```" in response:
                    parts = response.split("```")
                    if len(parts) >= 3:
                        json_str = parts[1].strip()
                        response_json = json.loads(json_str)
                        args[1] = response_json
                        return func(*args, **kwargs)
            except (IndexError, json.JSONDecodeError):
                pass

            # Try to find JSON object in the response
            try:
                start_index = response.find('{')
                end_index = response.rfind('}')
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    json_str = response[start_index:end_index+1]
                    response_json = json.loads(json_str)
                    args[1] = response_json
                    return func(*args, **kwargs)
            except json.JSONDecodeError:
                pass

            # Try to parse each line as JSON
            for line in response.splitlines():
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        response_json = json.loads(line)
                        args[1] = response_json
                        return func(*args, **kwargs)
                    except json.JSONDecodeError:
                        continue

            # If all else fails, return False
            emit_agent("info", {"type": "error", "message": "Failed to parse response as JSON"})
            return False

        except Exception as e:
            emit_agent("info", {"type": "error", "message": f"Error in response validation: {str(e)}"})
            return False

    return wrapper