import toml

class Config:
    def __init__(self):
        self.config = toml.load("config.toml")

    def get_config(self):
        return self.config

    def get_bing_api_key(self):
        return self.config["API_KEYS"]["BING"]
    
    def get_bing_api_endpoint(self):
        return self.config["API_ENDPOINTS"]["BING"]
    
    def get_google_search_api_key(self):
        return self.config["API_KEYS"]["GOOGLE_SEARCH"]

    def get_google_search_engine_id(self):
        return self.config["API_KEYS"]["GOOGLE_SEARCH_ENGINE_ID"]
    
    def get_google_search_api_endpoint(self):
        return self.config["API_ENDPOINTS"]["GOOGLE_SEARCH"]
    
    def get_claude_api_key(self):
        return self.config["API_KEYS"]["CLAUDE"]
    
    def get_openai_api_key(self):
        return self.config["API_KEYS"]["OPENAI"]
    
    def get_gemini_api_key(self):
        return self.config["API_KEYS"]["GEMINI"]
    
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
        
    def set_claude_api_key(self, key):
        self.config["API_KEYS"]["CLAUDE"] = key
        self.save_config()

    def set_openai_api_key(self, key):
        self.config["API_KEYS"]["OPENAI"] = key
        self.save_config()

    def set_gemini_api_key(self, key):
        self.config["API_KEYS"]["GEMINI"] = key
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

    def save_config(self):
        with open("config.toml", "w") as f:
            toml.dump(self.config, f)
