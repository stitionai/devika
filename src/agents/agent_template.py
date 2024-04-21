import json
import re
import os
import inspect
import logging

from jinja2 import BaseLoader, Environment


class AgentTemplate:
    """ "
    This class is the parent class of all the agents. It defines the methods and attributes common to all agents.
    """

    def __init__(self):
        pass

    def render(self, **kwargs) -> str:
        """
        This method renders the prompt template of the child class with the provided arguments.

        Args:
            **kwargs: The arguments to provide to the prompt template.

        Returns:
            str: The rendered prompt.
        """
        # Load the prompt template of the child class
        env = Environment(loader=BaseLoader())
        template_path = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), "prompt.jinja2"
        )
        with open(template_path, "r") as f:
            template_string = f.read()
            template = env.from_string(template_string)

        # Check if all the variables in the template are provided
        required_variables = re.findall(r"{{ (.*?) }}", template_string)
        for variable in required_variables:
            if variable not in kwargs:
                raise ValueError(f"Missing variable {variable} in the render method.")

        return template.render(**kwargs)

    def validate_response(self, response: str) -> dict | bool:
        """
        This method try to parse the response from the model to a dict based on the prompt structure.
        If it fails, it returns False.

        Args:
            response (str): The raw response from the model.

        Returns:
            dict | bool: The parsed response or False.
        """
        try:
            final_json = self.find_json_blocks(response)
        except Exception as _:
            return False

        try:
            final_json = json.loads(final_json)
        except Exception as _:
            return False

        # Get required fields from the response
        with open(
            os.path.join(
                os.path.dirname(inspect.getfile(self.__class__)), "prompt.jinja2"
            ),
            "r",
        ) as f:
            template = f.read()
        template_json = self.find_json_blocks(template)
        required_fields = list(json.loads(template_json).keys())

        # Check if all the required fields are present in the response
        for field in required_fields:
            if field not in final_json:
                logging.warning(f"Missing field {field} in the response.")
                return False

        return {field: final_json[field] for field in required_fields}

    def find_json_blocks(self, text: str) -> str:
        """
        This method extracts the JSON blocks from the text.

        Args:
            text (str): The text to extract the JSON blocks from.

        Returns:
            str: The extracted JSON blocks as a string that can be parsed using `json.loads`.

        Raises:
            Exception: If the JSON blocks cannot be parsed.
        """
        # Remove eventually unrendered jinja2 blocks and extract JSON blocks
        json_blocks = re.findall(r"{(.*?)}", re.sub(r"{{.*?}}", "", text), re.DOTALL)

        try:
            parsed_json_results = []
            for block in json_blocks:
                cleaned_block = block.replace("\n", "").replace("```\n\n```", "")
                parsed_block = json.loads("{" + cleaned_block + "}")
                parsed_json_results.append(parsed_block)
        except Exception as e:
            logging.warning(f"Error while parsing JSON blocks: {e}")
            raise e

        # Try to merge all the JSON blocks into a single JSON dict
        try:
            final_json = {}
            for parsed_block in parsed_json_results:
                for key, value in parsed_block.items():
                    if key in final_json:
                        final_json[key] += value
                    else:
                        final_json[key] = value

            final_json = json.dumps(final_json, indent=4)
        except Exception as e:
            logging.warning(f"Error while merging JSON blocks: {e}")
            raise e

        return final_json
