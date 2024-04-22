import os
from io import BytesIO
from markdown import markdown
from xhtml2pdf import pisa
from src.config import Config

class PDF:
    def __init__(self):
        config = Config()
        self.pdf_path = config.get_pdfs_dir()
    
    def markdown_to_pdf(self, markdown_string, project_name):
        html_string = markdown(markdown_string)
        
        out_file_path = os.path.join(self.pdf_path, f"{project_name}.pdf")
        with open(out_file_path, "wb") as out_file:
            pisa_status = pisa.CreatePDF(html_string, dest=out_file)

        if pisa_status.err:
            raise Exception("Error generating PDF")

        return out_file_path