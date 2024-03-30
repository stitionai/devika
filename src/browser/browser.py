import os

from playwright.sync_api import sync_playwright, TimeoutError
from markdownify import markdownify as md
from pdfminer.high_level import extract_text

from src.config import Config
from src.state import AgentState

class Browser:
    def __init__(self):
        self.playwright = sync_playwright().start()
        chromium = self.playwright.chromium
        self.browser = chromium.launch()
        self.page = self.browser.new_page()

    def new_page(self):
        return self.browser.new_page()

    def go_to(self, url):
        try:
            self.page.goto(url, timeout=30000)
        except TimeoutError as e:
            print(f"TimeoutError: {e} when trying to navigate to {url}")
            return False
        return True

    def screenshot(self, project_name):
        screenshots_save_path = Config().get_screenshots_dir()

        page_metadata = self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
        page_url = page_metadata['url']
        random_filename = os.urandom(20).hex()
        filename_to_save = f"{random_filename}.png"
        path_to_save = os.path.join(screenshots_save_path, filename_to_save)

        self.page.emulate_media(media="screen")
        self.page.screenshot(path=path_to_save)

        new_state = AgentState().new_state()
        new_state["internal_monologue"] = "Browsing the web right now..."
        new_state["browser_session"]["url"] = page_url
        new_state["browser_session"]["screenshot"] = path_to_save
        AgentState().add_to_current_state(project_name, new_state)        

        return path_to_save
    
    def get_html(self):
        return self.page.content()

    def get_markdown(self):
        return md(self.page.content())

    def get_pdf(self):
        pdfs_save_path = Config().get_pdfs_dir()
        
        page_metadata = self.page.evaluate("() => { return { url: document.location.href, title: document.title } }")
        filename_to_save = f"{page_metadata['title']}.pdf"
        save_path = os.path.join(pdfs_save_path, filename_to_save)
        
        self.page.pdf(path=save_path)        
        
        return save_path

    def pdf_to_text(self, pdf_path):
        return extract_text(pdf_path).strip()

    def get_content(self):
        pdf_path = self.get_pdf()
        return self.pdf_to_text(pdf_path)

    def extract_text(self):
        return self.page.evaluate("() => document.body.innerText")    

    def close(self):
        self.page.close()
        self.browser.close()
        self.playwright.stop()
