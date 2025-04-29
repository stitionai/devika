import os
from src.config import Config
from src.logger import Logger


def init_devika():
    """Initialize Devika by setting up necessary configurations and prerequisites.
    
    This function initializes Devika by performing several tasks: - Setting up logging. - Retrieving configuration settings
    such as database paths, directories for screenshots, PDFs, projects, and logs. - Creating the necessary directories if
    they do not exist. - Loading a sentence-transformer BERT model for keyword extraction.
    """
    logger = Logger()

    logger.info("Initializing Devika...")
    logger.info("checking configurations...")
    
    config = Config()

    sqlite_db = config.get_sqlite_db()
    screenshots_dir = config.get_screenshots_dir()
    pdfs_dir = config.get_pdfs_dir()
    projects_dir = config.get_projects_dir()
    logs_dir = config.get_logs_dir()

    logger.info("Initializing Prerequisites Jobs...")
    os.makedirs(os.path.dirname(sqlite_db), exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(projects_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    from src.bert.sentence import SentenceBert

    logger.info("Loading sentence-transformer BERT models...")
    prompt = "Light-weight keyword extraction exercise for BERT model loading.".strip()
    SentenceBert(prompt).extract_keywords()
    logger.info("BERT model loaded successfully.")
