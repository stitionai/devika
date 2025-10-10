import os
import shutil
import unittest
from src.filesystem.read_code import ReadCode
from src.config import Config

class TestReadCode(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.test_project = "test_project"
        self.project_dir = os.path.join(self.config.get_projects_dir(), self.test_project)

        # Create test project directory and files
        os.makedirs(self.project_dir, exist_ok=True)
        self.test_code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b

def multiply_numbers(x: int, y: int) -> int:
    """Multiply two numbers together."""
    return x * y
'''
        with open(os.path.join(self.project_dir, "test.py"), "w") as f:
            f.write(self.test_code)

        self.reader = ReadCode(self.test_project)

    def test_read_directory(self):
        files = self.reader.read_directory()
        self.assertEqual(len(files), 1)
        self.assertTrue(any(f["filename"].endswith("test.py") for f in files))
        self.assertTrue(any("calculate_sum" in f["code"] for f in files))

    def test_code_set_to_markdown(self):
        markdown = self.reader.code_set_to_markdown()
        self.assertIn("test.py", markdown)
        self.assertIn("```", markdown)
        self.assertIn("calculate_sum", markdown)
        self.assertIn("Summary:", markdown)

    def test_get_code_context(self):
        context = self.reader.get_code_context("How to multiply numbers?")
        self.assertTrue("relevant_code" in context)
        self.assertTrue("summary" in context)
        self.assertTrue(any("multiply" in code["code"].lower()
                          for code in context["relevant_code"]))

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.project_dir):
            shutil.rmtree(self.project_dir)
        # Clean up vector database
        vector_db_path = os.path.join(self.config.get_projects_dir(), ".vector_db")
        if os.path.exists(vector_db_path):
            shutil.rmtree(vector_db_path)

if __name__ == '__main__':
    unittest.main()
