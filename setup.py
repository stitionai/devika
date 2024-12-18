from setuptools import setup, find_packages

setup(
    name="devika",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "requests>=2.25.1",
        "pytest>=6.0.0",
    ],
    python_requires=">=3.8",
)
