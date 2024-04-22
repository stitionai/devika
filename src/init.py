import os
from src.config import Config
from src.logger import Logger


def init_devika():
    config = Config()
    logger = Logger()

    logger.info("Initializing devika...")
    sqlite_db = config.get_sqlite_db()
    screenshots_dir = config.get_screenshots_dir()
    pdfs_dir = config.get_pdfs_dir()
    projects_dir = config.get_projects_dir()
    logs_dir = config.get_logs_dir()

    logger.info("Initializing the model...")
    os.makedirs(os.path.dirname(sqlite_db), exist_ok=True)
    logger.info("initial check for errors...")
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)
    os.makedirs(projects_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    logger.info("no errors found proceeding...")
    from src.bert.sentence import SentenceBert

    logger.info("Loading the necessary files...")
    prompt = "Light-weight keyword extraction exercise for BERT model loading.".strip()
    SentenceBert(prompt).extract_keywords()
    logger.info("Files loaded successfully.")
