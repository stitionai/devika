import os
import sys

from src.config import Config
from src.logger import Logger

def init_cmd():
    config = Config()
    logger = Logger()
    command_line_args = sys.argv[1:]
    if '--websearch' in command_line_args:
        index = command_line_args.index('--websearch')
        websearch_value = command_line_args[index + 1]
        if(websearch_value == 'bing' or websearch_value == 'google' or websearch_value == 'ddgs'):
            config.set_web_search(websearch_value)
        else:
            return logger.error(f"Invalid websearch value parameter: {websearch_value}")
    else:
        logger.info("No --websearch argument provided. Using default duckduckgo search.")

def init_devika():
    config = Config()
    logger = Logger()

    logger.info("Initializing Devika...")
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

    init_cmd()
    logger.info(f"Using {config.get_web_search()} as default if not specified in the request.")

    from src.bert.sentence import SentenceBert

    logger.info("Loading sentence-transformer BERT models...")
    prompt = "Light-weight keyword extraction excercise for BERT model loading.".strip()
    SentenceBert(prompt).extract_keywords()
    logger.info("BERT model loaded successfully.")
