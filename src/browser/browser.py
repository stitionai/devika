import asyncio
import base64
import os

from playwright.async_api import async_playwright, TimeoutError
from markdownify import markdownify as md
from pdfminer.high_level import extract_text
from src.socket_instance import emit_agent
from src.config import Config
from src.state import AgentState
from src.logger import Logger


class Browser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.agent = AgentState()
        self.logger = Logger()

    async def start(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            return self
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            raise

    async def go_to(self, url):
        try:
            if not self.page:
                raise Exception("Browser not started")
                
            await self.page.goto(url, timeout=20000, wait_until='domcontentloaded')
            return True
        except TimeoutError as e:
            self.logger.error(f"TimeoutError: {e} when trying to navigate to {url}")
            return False
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False

    async def screenshot(self, project_name):
        try:
            if not self.page:
                raise Exception("Browser not started")
                
            screenshots_save_path = Config().get_screenshots_dir()

            page_metadata = await self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
            page_url = page_metadata.get('url', 'unknown')
            random_filename = os.urandom(20).hex()
            filename_to_save = f"{random_filename}.png"
            path_to_save = os.path.join(screenshots_save_path, filename_to_save)

            await self.page.emulate_media(media="screen")
            await self.page.screenshot(path=path_to_save, full_page=True)
            screenshot = await self.page.screenshot()
            screenshot_bytes = base64.b64encode(screenshot).decode()
            
            new_state = self.agent.new_state()
            new_state["internal_monologue"] = "Browsing the web right now..."
            new_state["browser_session"]["url"] = page_url
            new_state["browser_session"]["screenshot"] = path_to_save
            self.agent.add_to_current_state(project_name, new_state)
            
            return path_to_save, screenshot_bytes
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None, None

    async def get_html(self):
        try:
            if not self.page:
                raise Exception("Browser not started")
            return await self.page.content()
        except Exception as e:
            self.logger.error(f"Error getting HTML: {str(e)}")
            return ""

    async def get_markdown(self):
        try:
            html = await self.get_html()
            return md(html)
        except Exception as e:
            self.logger.error(f"Error converting to markdown: {str(e)}")
            return ""

    async def get_pdf(self):
        try:
            if not self.page:
                raise Exception("Browser not started")
                
            pdfs_save_path = Config().get_pdfs_dir()

            page_metadata = await self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
            title = page_metadata.get('title', 'untitled')
            # Sanitize filename
            title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename_to_save = f"{title}.pdf"
            save_path = os.path.join(pdfs_save_path, filename_to_save)

            await self.page.pdf(path=save_path)
            return save_path
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            return None

    def pdf_to_text(self, pdf_path):
        try:
            return extract_text(pdf_path).strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    async def get_content(self):
        try:
            pdf_path = await self.get_pdf()
            if pdf_path:
                return self.pdf_to_text(pdf_path)
            return ""
        except Exception as e:
            self.logger.error(f"Error getting content: {str(e)}")
            return ""

    async def extract_text(self):
        try:
            if not self.page:
                raise Exception("Browser not started")
            return await self.page.evaluate("() => document.body.innerText")
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return ""

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")