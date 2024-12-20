# ASCII Browser Integration

This document describes the ASCII browser integration in Devika using w3m.

## Overview

The ASCII browser implementation provides a lightweight alternative to API-based web access and screenshot-based browsing. It uses w3m to render web pages in ASCII format, which is both efficient and suitable for LLM processing.

## Requirements

- w3m must be installed on the system (`apt-get install w3m`)
- Python 3.6+ with subprocess module

## Usage

```python
from src.browser.w3m_browser import W3MBrowser

# Initialize browser
browser = W3MBrowser()

# Navigate to a URL
success, content = browser.navigate("http://example.com")

# Get current content
current_content = browser.get_current_content()
```

## Benefits

1. No API costs or rate limits
2. No third-party dependencies for basic web access
3. Efficient text-based content suitable for LLM processing
4. Reduced bandwidth usage compared to full browser rendering

## Limitations

1. No JavaScript support
2. Limited rendering of complex layouts
3. No image support in ASCII mode

## Error Handling

The browser implementation includes robust error handling for:
- Missing w3m installation
- Navigation failures
- Invalid URLs

## Installation

To install w3m on Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install w3m
```
