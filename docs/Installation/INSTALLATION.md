# Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/stitionai/devika.git
cd devika
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Common Issues

### Missing numpy dependency
If you encounter an error about numpy not being available, install it explicitly:
```bash
pip install numpy>=1.24.0
```

## Troubleshooting
If you encounter any installation issues:
1. Ensure you have Python 3.8 or higher installed
2. Try upgrading pip: `pip install --upgrade pip`
3. Install numpy explicitly if needed: `pip install numpy>=1.24.0`
