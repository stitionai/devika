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
        # If the config file doesn't exist, copy from the sample
        if not os.path.exists("config.toml"):
            with open("sample.config.toml", "r") as f_in, open("config.toml", "w+") as f_out:
                f_out.write(f_in.read())
                f_out.seek(0)
                self.config = toml.load(f_out)
        else:
            # check if all the keys are present in the config file
            with open("sample.config.toml", "r") as f:
                sample_config = toml.load(f)
            
            with open("config.toml", "r+") as f:
                config = toml.load(f)
            
                # Update the config with any missing keys and their keys of keys
                for key, value in sample_config.items():
                    config.setdefault(key, value)
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            config[key].setdefault(sub_key, sub_value)
            
                f.seek(0)
                toml.dump(config, f)
                f.truncate()
        
            self.config = config
            
    def get_config(self):
        return self.config

    def get_bing_api_endpoint(self):
        return self.config["API_ENDPOINTS"]["BING"]

    def get_bing_api_key(self):
        return self.config["API_KEYS"]["BING"]

    def get_google_search_api_key(self):
        return self.config["API_KEYS"]["GOOGLE_SEARCH"]

    def get_google_search_engine_id(self):
        return self.config["API_KEYS"]["GOOGLE_SEARCH_ENGINE_ID"]

    def get_google_search_api_endpoint(self):
        return self.config["API_ENDPOINTS"]["GOOGLE"]

    def get_ollama_api_endpoint(self):
        return self.config["API_ENDPOINTS"]["OLLAMA"]

    def get_claude_api_key(self):
        return self.config["API_KEYS"]["CLAUDE"]

    def get_openai_api_key(self):
        return self.config["API_KEYS"]["OPENAI"]

    def get_openai_api_base_url(self):
        return self.config["API_ENDPOINTS"]["OPENAI"]

    def get_gemini_api_key(self):
        return self.config["API_KEYS"]["GEMINI"]

    def get_mistral_api_key(self):
        return self.config["API_KEYS"]["MISTRAL"]

    def get_groq_api_key(self):
        return self.config["API_KEYS"]["GROQ"]

    def get_netlify_api_key(self):
        return self.config["API_KEYS"]["NETLIFY"]

    def get_sqlite_db(self):
        return self.config["STORAGE"]["SQLITE_DB"]

    def get_screenshots_dir(self):
        return self.config["STORAGE"]["SCREENSHOTS_DIR"]

    def get_pdfs_dir(self):
        return self.config["STORAGE"]["PDFS_DIR"]

    def get_projects_dir(self):
        return self.config["STORAGE"]["PROJECTS_DIR"]

    def get_logs_dir(self):
        return self.config["STORAGE"]["LOGS_DIR"]

    def get_repos_dir(self):
        return self.config["STORAGE"]["REPOS_DIR"]

    def get_logging_rest_api(self):
        return self.config["LOGGING"]["LOG_REST_API"] == "true"

    def get_logging_prompts(self):
        return self.config["LOGGING"]["LOG_PROMPTS"] == "true"
    
    def get_timeout_inference(self):
        return self.config["TIMEOUT"]["INFERENCE"]

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

    def set_openai_api_endpoint(self,endpoint):
        self.config["API_ENDPOINTS"]["OPENAI"] = endpoint
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

    def set_logging_rest_api(self, value):
        self.config["LOGGING"]["LOG_REST_API"] = "true" if value else "false"
        self.save_config()

    def set_logging_prompts(self, value):
        self.config["LOGGING"]["LOG_PROMPTS"] = "true" if value else "false"
        self.save_config()

    def set_timeout_inference(self, value):
        self.config["TIMEOUT"]["INFERENCE"] = value
        self.save_config()

    def save_config(self):
        with open("config.toml", "w") as f:
            toml.dump(self.config, f)

    def update_config(self, data):
        for key, value in data.items():
            if key in self.config:
                with open("config.toml", "r+") as f:
                    config = toml.load(f)
                    for sub_key, sub_value in value.items():
                        self.config[key][sub_key] = sub_value
                        config[key][sub_key] = sub_value
                    f.seek(0)
                    toml.dump(config, f)
