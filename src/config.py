import os

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

    def try_get(self, *keys):
        try:
            value = self.config
            for key in keys:
                value = value[key]

            return value, None, None
        except KeyError as e:
            sample = "Some value"
            for key in reversed(keys):
                sample = {key: sample}

            err = f"Key {e} of {'.'.join(keys)} not found in config.toml using 'None' as default value"
            fix = f"To fix this, update 'config.toml' with\n\n{toml.dumps(sample)}\n"
            return None, err, fix

    def try_get_with_warning(self, *keys):
        value, err, fix = self.try_get(*keys)
        if err:
            self._logger.warning(err)
            self._logger.info(fix)
        return value

    def try_get_with_error(self, *keys):
        value, err, fix = self.try_get(*keys)
        if err:
            self._logger.error(err)
            self._logger.info(fix)
            exit(1)
        return value

    def get_config(self):
        return self.config

    def get_bing_api_endpoint(self):
        return self.try_get_with_error("API_ENDPOINTS", "BING")

    def get_bing_api_key(self):
        return self.try_get_with_error("API_KEYS", "BING")

    def get_google_search_api_key(self):
        return self.try_get_with_error("API_KEYS", "GOOGLE_SEARCH")

    def get_google_search_engine_id(self):
        return self.try_get_with_error("API_KEYS", "GOOGLE_SEARCH_ENGINE_ID")

    def get_google_search_api_endpoint(self):
        return self.try_get_with_error("API_ENDPOINTS", "GOOGLE")

    def get_ollama_api_endpoint(self):
        return self.try_get_with_error("API_ENDPOINTS", "OLLAMA")

    def get_claude_api_key(self):
        return self.try_get_with_error("API_KEYS", "CLAUDE")

    def get_openai_api_key(self):
        return self.try_get_with_error("API_KEYS", "OPENAI")

    def get_gemini_api_key(self):
        return self.try_get_with_error("API_KEYS", "GEMINI")

    def get_mistral_api_key(self):
        return self.try_get_with_error("API_KEYS", "MISTRAL")

    def get_groq_api_key(self):
        return self.try_get_with_error("API_KEYS", "GROQ")

    def get_netlify_api_key(self):
        return self.try_get_with_error("API_KEYS", "NETLIFY")

    def get_sqlite_db(self):
        return self.try_get_with_error("STORAGE", "SQLITE_DB")

    def get_screenshots_dir(self):
        return self.try_get_with_error("STORAGE", "SCREENSHOTS_DIR")

    def get_pdfs_dir(self):
        return self.try_get_with_error("STORAGE", "PDFS_DIR")

    def get_projects_dir(self):
        return self.try_get_with_error("STORAGE", "PROJECTS_DIR")

    def get_logs_dir(self):
        return self.try_get_with_error("STORAGE", "LOGS_DIR")

    def get_repos_dir(self):
        return self.try_get_with_error("STORAGE", "REPOS_DIR")

    def get_logging_rest_api(self):
        return self.try_get_with_warning("LOGGING", "LOG_REST_API") == "true"

    def get_logging_prompts(self):
        return self.try_get_with_warning("LOGGING", "LOG_PROMPTS") == "true"

    def set_bing_api_key(self, key):
        self.config["API_KEYS"]["BING"] = key
        self.save_config()

    def set_bing_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS"]["BING"] = endpoint
        self.save_config()

    def set_google_search_api_key(self, key):
        self.config["API_KEYS"]["GOOGLE_SEARCH"] = key
        self.save_config()

    def set_google_search_engine_id(self, key):
        self.config["API_KEYS"]["GOOGLE_SEARCH_ENGINE_ID"] = key
        self.save_config()

    def set_google_search_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS"]["GOOGLE_SEARCH"] = endpoint
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

    def set_gemini_api_key(self, key):
        self.config["API_KEYS"]["GEMINI"] = key
        self.save_config()

    def set_mistral_api_key(self, key):
        self.config["API_KEYS"]["MISTRAL"] = key
        self.save_config()

    def set_groq_api_key(self, key):
        self.config["API_KEYS"]["GROQ"] = key
        self.save_config()

    def set_netlify_api_key(self, key):
        self.config["API_KEYS"]["NETLIFY"] = key
        self.save_config()

    def set_sqlite_db(self, db):
        self.config["STORAGE"]["SQLITE_DB"] = db
        self.save_config()

    def set_screenshots_dir(self, directory):
        self.config["STORAGE"]["SCREENSHOTS_DIR"] = directory
        self.save_config()

    def set_pdfs_dir(self, directory):
        self.config["STORAGE"]["PDFS_DIR"] = directory
        self.save_config()

    def set_projects_dir(self, directory):
        self.config["STORAGE"]["PROJECTS_DIR"] = directory
        self.save_config()

    def set_logs_dir(self, directory):
        self.config["STORAGE"]["LOGS_DIR"] = directory
        self.save_config()

    def set_repos_dir(self, directory):
        self.config["STORAGE"]["REPOS_DIR"] = directory
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
