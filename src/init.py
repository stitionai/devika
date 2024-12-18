import os
import importlib.util

# Validate numpy dependency first
try:
    import numpy
    print(f"numpy version {numpy.__version__} found")
except ImportError:
    raise ImportError(
        "numpy is required but not installed. Please install it using:\n"
        "pip install numpy>=1.24.0"
    )

from src.config import Config
from src.logger import Logger


def init_devika():
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
