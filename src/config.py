import os
from os import environ

import toml
from fastlogging import LogInit
from toml import TomlDecodeError


class Config:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance:
            return cls._instance

        cls._instance = super().__new__(cls)
        cls._logger = LogInit(pathName="logs/core.log", console=True, colors=True)

        try:
            cls._instance.config = toml.load("config.toml")
            return cls._instance

        except FileNotFoundError as e:
            cls._logger.critical(f"Configuration file '{os.path.join(os.getcwd(), e.filename)}' not found")
            cls._logger.info(f"Did you forget to create 'config.toml' file at the project root ( {os.getcwd()} )?")
        except TomlDecodeError as e:
            cls._logger.critical(f"There is something wrong with your 'config.toml' file: {e}")

        cls._logger.info("Checkout 'config.example.toml' and https://toml.io/en/ for more information on TOML.")
        exit(1)

    def get_config(self):
        return self.config

    def try_get_with_warning(self, *keys):
        try:
            value = self.config
            for key in keys:
                value = value[key]

            return value
        except KeyError as e:
            sample = "Some value"
            for key in reversed(keys):
                sample = {key: sample}

            self._logger.warning(f"Key {e} of {'.'.join(keys)} not found in config.toml using 'None' as default value")
            self._logger.info(f"To fix this, update 'config.toml' with\n\n{toml.dumps(sample)}\n")
            return None

    def get_bing_api_key(self):
        return environ.get("BING_API_KEY", self.try_get_with_warning("API_KEYS", "BING"))

    def get_bing_api_endpoint(self):
        return environ.get("BING_API_ENDPOINT", self.try_get_with_warning("API_ENDPOINTS", "BING"))

    def get_ollama_api_endpoint(self):
        return environ.get("OLLAMA_API_ENDPOINT", self.try_get_with_warning("API_ENDPOINTS", "OLLAMA"))

    def get_claude_api_key(self):
        return environ.get("CLAUDE_API_KEY", self.try_get_with_warning("API_KEYS", "CLAUDE"))

    def get_openai_api_key(self):
        return environ.get("OPENAI_API_KEY", self.try_get_with_warning("API_KEYS", "OPENAI"))

    def get_netlify_api_key(self):
        return environ.get("NETLIFY_API_KEY", self.try_get_with_warning("API_KEYS", "NETLIFY"))

    def get_groq_api_key(self):
        return environ.get("GROQ_API_KEY", self.try_get_with_warning("API_KEYS", "GROQ"))

    def get_sqlite_db(self):
        return environ.get("SQLITE_DB_PATH", self.try_get_with_warning("STORAGE", "SQLITE_DB"))

    def get_screenshots_dir(self):
        return environ.get("SCREENSHOTS_DIR", self.try_get_with_warning("STORAGE", "SCREENSHOTS_DIR"))

    def get_pdfs_dir(self):
        return environ.get("PDFS_DIR", self.try_get_with_warning("STORAGE", "PDFS_DIR"))

    def get_projects_dir(self):
        return environ.get("PROJECTS_DIR", self.try_get_with_warning("STORAGE", "PROJECTS_DIR"))

    def get_logs_dir(self):
        return environ.get("LOGS_DIR", self.try_get_with_warning("STORAGE", "LOGS_DIR"))

    def get_repos_dir(self):
        return environ.get("REPOS_DIR", self.try_get_with_warning("STORAGE", "REPOS_DIR"))

    def get_logging_rest_api(self):
        return self.config["LOGGING"]["LOG_REST_API"] == "true"

    def get_logging_prompts(self):
        return self.config["LOGGING"]["LOG_PROMPTS"] == "true"

    def set_bing_api_key(self, key):
        self.config["API_KEYS"]["BING"] = key
        self.save_config()

    def set_bing_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS"]["BING"] = endpoint
        self.save_config()

    def set_ollama_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS"]["OLLAMA"] = endpoint
        self.save_config()

    def set_claude_api_key(self, key):
        self.config["API_KEYS"]["CLAUDE"] = key
        self.save_config()

    def set_openai_api_key(self, key):
        self.config["API_KEYS"]["OPENAI"] = key
        self.save_config()

    def set_netlify_api_key(self, key):
        self.config["API_KEYS"]["NETLIFY"] = key
        self.save_config()

    def set_sqlite_db(self, db):
        self.config["STORAGE"]["SQLITE_DB"] = db
        self.save_config()

    def set_screenshots_dir(self, dir):
        self.config["STORAGE"]["SCREENSHOTS_DIR"] = dir
        self.save_config()

    def set_pdfs_dir(self, dir):
        self.config["STORAGE"]["PDFS_DIR"] = dir
        self.save_config()

    def set_projects_dir(self, dir):
        self.config["STORAGE"]["PROJECTS_DIR"] = dir
        self.save_config()

    def set_logs_dir(self, dir):
        self.config["STORAGE"]["LOGS_DIR"] = dir
        self.save_config()

    def set_repos_dir(self, dir):
        self.config["STORAGE"]["REPOS_DIR"] = dir
        self.save_config()

    def set_logging_rest_api(self, value):
        self.config["LOGGING"]["LOG_REST_API"] = "true" if value else "false"
        self.save_config()

    def set_logging_prompts(self, value):
        self.config["LOGGING"]["LOG_PROMPTS"] = "true" if value else "false"
        self.save_config()

    def save_config(self):
        with open("config.toml", "w") as f:
            toml.dump(self.config, f)
