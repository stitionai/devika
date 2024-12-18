import unittest
from src.memory.rag import CodeRAG

class TestCodeRAG(unittest.TestCase):
    def setUp(self):
        self.test_project = "test_project"
        self.rag = CodeRAG(self.test_project)

        # Test code sample
        self.test_code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b

def multiply_numbers(x: int, y: int) -> int:
    """Multiply two numbers together."""
    return x * y
'''

    def test_chunk_code(self):
        """Test code chunking functionality."""
        chunks = self.rag.chunk_code(self.test_code, chunk_size=100)
        self.assertTrue(len(chunks) > 0)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))
        # Verify function boundaries are preserved
        self.assertTrue(any("calculate_sum" in chunk for chunk in chunks))
        self.assertTrue(any("multiply_numbers" in chunk for chunk in chunks))

if __name__ == '__main__':
    unittest.main()
