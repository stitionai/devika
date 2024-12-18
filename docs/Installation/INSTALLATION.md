# Comprehensive Installation Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Version Requirements](#version-requirements)
- [Installation Methods](#installation-methods)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Package Dependencies](#package-dependencies)
- [Common Issues & Solutions](#common-issues--solutions)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing Devika, ensure you have the following tools installed:
- Git
- Python (see version requirements)
- Node.js (see version requirements)
- uv (Python package manager)
- bun (JavaScript runtime)

## Version Requirements

### Python Version Compatibility
- **Required**: Python >= 3.10 and < 3.12
- **Recommended**: Python 3.11
- **Note**: Python 3.12 support is planned but currently not available due to dependency constraints

### Node.js Version Compatibility
- **Required**: Node.js >= 18
- **Recommended**: Node.js 18.x LTS or 20.x LTS
- **Known Issues**:
  - Node.js 19.x may have compatibility issues with some SvelteKit dependencies
  - Node.js versions below 18 are not supported due to SvelteKit requirements

### Package Manager Requirements
- **uv**: Latest version recommended
- **bun**: Latest version required for optimal frontend development

## Installation Methods

### Local Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/stitionai/devika.git
cd devika
```

#### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
uv venv

# On macOS and Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# Install Python dependencies
uv pip install -r requirements.txt
```

#### 3. Install Browser Dependencies
```bash
# Install Playwright browsers and dependencies
playwright install --with-deps
```

#### 4. Set Up Frontend
```bash
cd ui/
bun install
```

### Docker Installation

Docker installation provides a containerized environment with all dependencies pre-configured.

#### Prerequisites
- Docker
- Docker Compose

#### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/stitionai/devika.git
   cd devika
   ```

2. Start the services:
   ```bash
   docker compose up -d
   ```

3. Access Devika at `http://localhost:3000`

#### Docker Configuration
The docker-compose.yaml file includes:
- Ollama service for local LLM support
- Backend service with API endpoints
- Frontend service with UI
- Persistent volume for database storage

## Package Dependencies

### Core Python Dependencies
- **flask**, **flask-cors**: Web server and CORS support
- **playwright**: Web automation and browsing capabilities
- **anthropic**, **openai**, **google-generativeai**: LLM API clients
- **ollama**: Local LLM integration
- **sqlmodel**: Database ORM
- **tiktoken**: Token counting for LLMs
- **keybert**: Keyword extraction
- **Flask-SocketIO**, **eventlet**: Real-time communication

### Frontend Dependencies
- **SvelteKit**: Web application framework
- **Tailwind CSS**: Styling
- **Monaco Editor**: Code editor component
- **Socket.io**: Real-time communication
- **xterm**: Terminal emulation

## Common Issues & Solutions

### Python Environment Issues

1. **NumPy Installation Errors**
   - **Issue**: `error: Microsoft Visual C++ 14.0 or greater is required`
   - **Solution**: Install Visual Studio Build Tools with C++ workload

2. **Playwright Installation**
   - **Issue**: Browser installation fails
   - **Solution**: Run `playwright install --with-deps` with admin privileges

### Node.js/Frontend Issues

1. **SvelteKit Build Errors**
   - **Issue**: `Error: Cannot find module '@sveltejs/kit'`
   - **Solution**: Clear node_modules and reinstall with `bun install`

2. **Vite Build Issues**
   - **Issue**: `Error: The requested module '/node_modules/...' does not provide an export named '...'`
   - **Solution**: Ensure Node.js version >= 18 is installed

### Docker Issues

1. **Container Start Failures**
   - **Issue**: Services fail to start
   - **Solution**: Check port conflicts and ensure Docker daemon is running

2. **Volume Permission Issues**
   - **Issue**: Database write permission errors
   - **Solution**: Check volume permissions in docker-compose.yaml

## Troubleshooting

### Installation Verification
Run these commands to verify your installation:

1. Check Python environment:
```bash
python --version
pip list
```

2. Verify Node.js setup:
```bash
node --version
bun --version
```

3. Test Devika services:
```bash
# Backend
python devika.py

# Frontend
cd ui/
bun run dev
```

### Debug Mode
To run Devika in debug mode:
```bash
# Backend with debug logging
python devika.py --debug

# Frontend with development server
cd ui/
bun run dev
```

### Logs Location
- Backend logs: `./logs/devika.log`
- Frontend build logs: `./ui/logs/`
- Docker logs: Use `docker compose logs`

For additional help, visit:
- [GitHub Issues](https://github.com/stitionai/devika/issues)
- [Discussions](https://github.com/stitionai/devika/discussions)
- [Discord Community](https://discord.gg/CYRp43878y)
