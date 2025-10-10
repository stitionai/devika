import os
import time
import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import ollama
from src.logger import Logger
from src.config import Config

log = Logger()

class Ollama:
    def __init__(self):
        """Initialize Ollama client with retry logic and proper error handling."""
        self.host = os.getenv("OLLAMA_HOST", Config().get_ollama_api_endpoint())
        self.client = None
        self.models = []
        self._initialize_client()

    def _initialize_client(self, max_retries: int = 3, initial_delay: float = 1.0) -> None:
        """Initialize Ollama client with retry logic.

        Args:
            max_retries: Maximum number of connection attempts
            initial_delay: Initial delay between retries in seconds
        """
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                # Validate URL format
                parsed_url = urlparse(self.host)
                if not parsed_url.scheme or not parsed_url.netloc:
                    raise ValueError(f"Invalid Ollama server URL: {self.host}")

                # Test server connection
                response = requests.get(f"{self.host}/api/version")
                if response.status_code != 200:
                    raise ConnectionError(f"Ollama server returned status {response.status_code}")

                # Initialize client and fetch models
                self.client = ollama.Client(self.host)
                self.models = self.client.list()["models"]
                log.info(f"Ollama available at {self.host}")
                log.info(f"Found {len(self.models)} models: {[m['name'] for m in self.models]}")
                return

            except requests.exceptions.ConnectionError as e:
                log.warning(f"Connection failed to Ollama server at {self.host}")
                log.warning(f"Error: {str(e)}")

            except ValueError as e:
                log.error(f"Configuration error: {str(e)}")
                return

            except Exception as e:
                log.warning(f"Failed to initialize Ollama client: {str(e)}")

            if attempt < max_retries - 1:
                log.info(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                log.warning("Max retries reached. Please ensure Ollama server is running")
                log.warning("Run 'ollama serve' to start the server")
                log.warning("Or set OLLAMA_HOST environment variable to correct server URL")

        self.client = None
        self.models = []

    def inference(self, model_id: str, prompt: str) -> str:
        """Run inference using specified model.

        Args:
            model_id: Name of the Ollama model to use
            prompt: Input prompt for the model

        Returns:
            Model response text

        Raises:
            RuntimeError: If client is not initialized or model is not found
        """
        if not self.client:
            raise RuntimeError("Ollama client not initialized. Please check server connection.")

        if not any(m['name'] == model_id for m in self.models):
            raise RuntimeError(f"Model {model_id} not found in available models: {[m['name'] for m in self.models]}")

        try:
            response = self.client.generate(
                model=model_id,
                prompt=prompt.strip(),
                options={"temperature": 0}
            )
            return response['response']

        except Exception as e:
            log.error(f"Inference failed for model {model_id}: {str(e)}")
            raise RuntimeError(f"Failed to get response from Ollama: {str(e)}")
