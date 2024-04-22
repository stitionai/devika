import toml
import os


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        if not os.path.exists("config.toml"):
            with open("sample.config.toml", "r") as f_in, open("config.toml", "w") as f_out:
                f_out.write(f_in.read())

        self.config = toml.load("config.toml")

    def get_config(self):
        return self.config

    def get_bing_api_endpoint(self):
        return self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["BING"]

    def get_bing_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["BING"]
    
    def get_google_search_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH"]

    def get_google_search_engine_id(self):
        return self.config["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH_ENGINE_ID"]

    def get_google_search_api_endpoint(self):
        return self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["GOOGLE"]
    
    def get_ollama_api_endpoint(self):
        return self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["OLLAMA"]

    def get_claude_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["CLAUDE"]

    def get_openai_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["OPENAI"]
    
    def get_openai_api_base_url(self):
        return self.config["API_KEYS_FOR_MODELS"]["OPENAI"]

    def get_gemini_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["GEMINI"]

    def get_mistral_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["MISTRAL"]

    def get_groq_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["GROQ"]

    def get_netlify_api_key(self):
        return self.config["API_KEYS_FOR_MODELS"]["NETLIFY"]

    def get_sqlite_db(self):
        return self.config["STORAGE_SYSTEM_FILES"]["SQLITE_DB"]

    def get_screenshots_dir(self):
        return self.config["STORAGE_SYSTEM_FILES"]["SCREENSHOTS_DIR"]

    def get_pdfs_dir(self):
        return self.config["STORAGE_SYSTEM_FILES"]["PDFS_DIR"]

    def get_projects_dir(self):
        return self.config["STORAGE_SYSTEM_FILES"]["PROJECTS_DIR"]

    def get_logs_dir(self):
        return self.config["STORAGE_SYSTEM_FILES"]["LOGS_DIR"]

    def get_repos_dir(self):
        return self.config["STORAGE_SYSTEM_FILES"]["REPOS_DIR"]

    def get_logging_rest_api(self):
        return self.config["LOGGING_DUMPS"]["LOG_REST_API"] == "true"

    def get_logging_prompts(self):
        return self.config["LOGGING_DUMPS"]["LOG_PROMPTS"] == "true"

    def set_bing_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["BING"] = key
        self.save_config()

    def set_bing_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["BING"] = endpoint
        self.save_config()

    def set_google_search_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH"] = key
        self.save_config()

    def set_google_search_engine_id(self, key):
        self.config["API_KEYS_FOR_MODELS"]["GOOGLE_SEARCH_ENGINE_ID"] = key
        self.save_config()

    def set_google_search_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["GOOGLE_SEARCH"] = endpoint
        self.save_config()

    def set_ollama_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS_FOR_ONLINE_SEARCHES"]["OLLAMA"] = endpoint
        self.save_config()

    def set_claude_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["CLAUDE"] = key
        self.save_config()

    def set_openai_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["OPENAI"] = key
        self.save_config()

    def set_gemini_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["GEMINI"] = key
        self.save_config()

    def set_mistral_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["MISTRAL"] = key
        self.save_config()

    def set_groq_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["GROQ"] = key
        self.save_config()

    def set_netlify_api_key(self, key):
        self.config["API_KEYS_FOR_MODELS"]["NETLIFY"] = key
        self.save_config()

    def set_sqlite_db(self, db):
        self.config["STORAGE_SYSTEM_FILES"]["SQLITE_DB"] = db
        self.save_config()

    def set_screenshots_dir(self, dir):
        self.config["STORAGE_SYSTEM_FILES"]["SCREENSHOTS_DIR"] = dir
        self.save_config()

    def set_pdfs_dir(self, dir):
        self.config["STORAGE_SYSTEM_FILES"]["PDFS_DIR"] = dir
        self.save_config()

    def set_projects_dir(self, dir):
        self.config["STORAGE_SYSTEM_FILES"]["PROJECTS_DIR"] = dir
        self.save_config()

    def set_logs_dir(self, dir):
        self.config["STORAGE_SYSTEM_FILES"]["LOGS_DIR"] = dir
        self.save_config()

    def set_repos_dir(self, dir):
        self.config["STORAGE_SYSTEM_FILES"]["REPOS_DIR"] = dir
        self.save_config()

    def set_logging_rest_api(self, value):
        self.config["LOGGING_DUMPS"]["LOG_REST_API"] = "true" if value else "false"
        self.save_config()

    def set_logging_prompts(self, value):
        self.config["LOGGING_DUMPS"]["LOG_PROMPTS"] = "true" if value else "false"
        self.save_config()



    def save_config(self):
        with open("config.toml", "w") as f:
            toml.dump(self.config, f)
