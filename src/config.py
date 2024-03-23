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
    
    def get_claude_api_key(self):
        return self.config["API_KEYS"]["CLAUDE"]
    
    def get_openai_api_key(self):
        return self.config["API_KEYS"]["OPENAI"]
    
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
    
    def get_openai_base_url(self):
        return self.config["API_ENDPOINTS"]["OPENAI_BASE_URL"]
    
    def get_search_engine(self):
        return self.config["USER_PREFS"]["SEARCH_ENGINE"]
    
    def set_bing_api_key(self, key):
        self.config["API_KEYS"]["BING"] = key
        self.save_config()

    def set_bing_api_endpoint(self, endpoint):
        self.config["API_ENDPOINTS"]["BING"] = endpoint
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

    def save_config(self):
        with open("config.toml", "w") as f:
            toml.dump(self.config, f)
