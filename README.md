<p align="center">
  <img src=".assets/devika-avatar.png" alt="Devika Logo" width="250">
</p>

<h1 align="center">🚀 Devika - Agentic AI Software Engineer 👩‍💻</h1>

![devika screenshot](.assets/devika-screenshot.png)

> [!IMPORTANT]  
> This project is currently in a very early development/experimental stage. There are a lot of unimplemented/broken features at the moment. Contributions are welcome to help out with the progress!

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [New Features](#new-features)
- [Web Interface Coding Editor](#web-interface-coding-editor)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [How to use](#how-to-use)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Help and Support](#help-and-support)
- [License](#license)

## About

Devika is an advanced AI software engineer that can understand high-level human instructions, break them down into steps, research relevant information, and write code to achieve the given objective. Devika utilizes large language models, planning and reasoning algorithms, and web browsing abilities to intelligently develop software.

Devika aims to revolutionize the way we build software by providing an AI pair programmer who can take on complex coding tasks with minimal human guidance. Whether you need to create a new feature, fix a bug, or develop an entire project from scratch, Devika is here to assist you.

> [!NOTE]
> Devika is modeled after [Devin](https://www.cognition-labs.com/introducing-devin) by Cognition AI. This project aims to be an open-source alternative to Devin with an "overly ambitious" goal to meet the same score as Devin in the [SWE-bench](https://www.swebench.com/) Benchmarks... and eventually beat it?

## Demos

https://github.com/stitionai/devika/assets/26198477/cfed6945-d53b-4189-9fbe-669690204206

## Key Features

- 🤖 Supports **Claude 3**, **GPT-4**, **Gemini**, **Mistral** , **Groq** and **Local LLMs** via [Ollama](https://ollama.com). For optimal performance: Use the **Claude 3** family of models.
- 🧠 Advanced AI planning and reasoning capabilities
- 🔍 Contextual keyword extraction for focused research
- 🌐 Seamless web browsing and information gathering
- 💻 Code writing in multiple programming languages
- 📊 Dynamic agent state tracking and visualization
- 💬 Natural language interaction via chat interface
- 📂 Project-based organization and management
- 🔌 Extensible architecture for adding new features and integrations

## New Features

### 🔍 Advanced Code Analysis
- **Code Review Agent**: Comprehensive code quality analysis with scoring and recommendations
- **Security Auditor**: Identifies vulnerabilities, security issues, and compliance concerns
- **Performance Optimizer**: Analyzes bottlenecks and suggests optimizations
- **Dependency Manager**: Checks for outdated packages, security vulnerabilities, and license conflicts

### 🛠️ Enhanced Development Tools
- **Test Generator**: Automatically creates unit tests, integration tests, and test suites
- **Documentation Generator**: Creates comprehensive API docs, README files, and user guides
- **Git Integration**: Enhanced version control with commit history and repository management

### 📊 Analysis Dashboard
- **Interactive Analysis Panel**: New UI component for running and viewing analysis results
- **Real-time Results**: Live updates of analysis progress and results
- **Visual Reports**: Color-coded severity levels and priority indicators

### 🎯 Improved Agent Actions
- **Extended Action Set**: New actions for `review`, `test`, `optimize`, `security`, `document`, and `dependencies`
- **Smart Action Detection**: Better understanding of user intent for automated task routing
- **Contextual Responses**: More detailed and actionable feedback from analysis results

### 🔧 Developer Experience
- **Enhanced Error Handling**: Better error messages and recovery mechanisms
- **Improved Logging**: More detailed analysis and operation logs
- **API Endpoints**: RESTful APIs for programmatic access to analysis features

## Web Interface Coding Editor

### 🖥️ Professional Code Editor
- **Monaco Editor Integration**: Full-featured code editor with syntax highlighting for 50+ languages
- **Intelligent Code Completion**: Context-aware suggestions and auto-completion
- **Multi-tab Support**: Work on multiple files simultaneously with tab management
- **File Explorer**: Tree view of project files with context menu operations
- **Real-time Collaboration**: Live editing with conflict resolution

### ⚡ Advanced Editor Features
- **Syntax Highlighting**: Support for JavaScript, TypeScript, Python, HTML, CSS, and more
- **Code Formatting**: Automatic code formatting with Prettier integration
- **Error Detection**: Real-time syntax and semantic error highlighting
- **Find & Replace**: Advanced search with regex support and multi-file search
- **Code Folding**: Collapse and expand code blocks for better navigation
- **Minimap**: Bird's eye view of the entire file for quick navigation

### 🎨 Customizable Interface
- **Theme Support**: Light and dark themes with custom color schemes
- **Font Customization**: Adjustable font size and family preferences
- **Layout Options**: Resizable panels and customizable workspace layout
- **Keyboard Shortcuts**: Extensive keyboard shortcuts for power users
- **Status Bar**: Real-time information about cursor position, file encoding, and language

### 📁 File Management
- **Create/Delete Files**: Easy file and folder creation with context menus
- **Rename Operations**: Inline renaming with validation
- **File Upload**: Drag and drop file upload support
- **Auto-save**: Automatic saving with visual indicators for unsaved changes
- **Version Control**: Git integration with diff viewing and commit history

### 🔧 Developer Tools
- **Integrated Terminal**: Built-in terminal for running commands
- **Debugging Support**: Breakpoints and step-through debugging
- **Extension System**: Plugin architecture for custom functionality
- **Code Snippets**: Predefined code templates and custom snippets
- **Emmet Support**: Fast HTML/CSS coding with Emmet abbreviations

## System Architecture

Read [**README.md**](docs/architecture) for the detailed documentation.

## Getting Started

### Requirements
```
Version's requirements
  - Python >= 3.10 and < 3.12
  - NodeJs >= 18
  - bun
```

- Install uv - Python Package manager [download](https://github.com/astral-sh/uv)
- Install bun - JavaScript runtime [download](https://bun.sh/docs/installation)
- For ollama [ollama setup guide](docs/Installation/ollama.md) (optinal: if you don't want to use the local models then you can skip this step)
- For API models, configure the API keys via setting page in UI.

### Installation

To install Devika, follow these steps:

1. Clone the Devika repository:
   ```bash
   git clone https://github.com/stitionai/devika.git
   ```
2. Navigate to the project directory:
   ```bash
   cd devika
   ```
3. Create a virtual environment and install the required dependencies (you can use any virtual environment manager):
   ```bash
   uv venv
   
   # On macOS and Linux.
   source .venv/bin/activate

   # On Windows.
   .venv\Scripts\activate

   uv pip install -r requirements.txt
   ```
4. Install the playwright for browsering capabilities:
   ```bash
   playwright install --with-deps # installs browsers in playwright (and their deps) if required
   ```
5. Start the Devika server:
   ```bash
   python devika.py
   ```
6. if everything is working fine, you see the following output:
   ```bash
   root: INFO   : Devika is up and running!
   ```
7. Now, for frontend, open a new terminal and navigate to the `ui` directory:
   ```bash
   cd ui/
   bun install
   bun run start
   ```
8. Access the Devika web interface by opening a browser and navigating to `http://127.0.0.1:3001`

### how to use

To start using Devika, follow these steps:

1. Open the Devika web interface in your browser.
2. To create a project, click on 'select project' and then click on 'new project'.
3. Select the search engine and model configuration for your project.
4. In the chat interface, provide a high-level objective or task description for Devika to work on.
5. Devika will process your request, break it down into steps, and start working on the task.
6. Monitor Devika's progress, view generated code, and provide additional guidance or feedback as needed.
7. Use the new Analysis Panel to run code reviews, security audits, performance analysis, and dependency checks.
8. Generate tests and documentation using the enhanced tools.
9. **Use the Web Code Editor** to manually edit files, create new files, and manage your project structure.
10. Once Devika completes the task, review the generated code and project files.
11. Iterate and refine the project as desired by providing further instructions or modifications.

### Web Code Editor Usage

1. **Access the Editor**: Click on the "Code Editor" icon in the sidebar to open the web-based code editor.
2. **File Management**: Use the file explorer on the left to navigate, create, delete, and rename files.
3. **Multi-tab Editing**: Open multiple files in tabs for efficient development workflow.
4. **Code Features**: Enjoy syntax highlighting, auto-completion, and error detection.
5. **Save Changes**: Use Ctrl+S to save files or enable auto-save in settings.
6. **Collaboration**: Work alongside Devika's AI-generated code with real-time updates.

## Configuration

Devika requires certain configuration settings and API keys to function properly:

when you first time run Devika, it will create a `config.toml` file for you in the root directory. You can configure the following settings in the settings page via UI:

- API KEYS
   - `BING`: Your Bing Search API key for web searching capabilities.
   - `GOOGLE_SEARCH`: Your Google Search API key for web searching capabilities.
   - `GOOGLE_SEARCH_ENGINE_ID`: Your Google Search Engine ID for web searching using Google.
   - `OPENAI`: Your OpenAI API key for accessing GPT models.
   - `GEMINI`: Your Gemini API key for accessing Gemini models.
   - `CLAUDE`: Your Anthropic API key for accessing Claude models.
   - `MISTRAL`: Your Mistral API key for accessing Mistral models.
   - `GROQ`: Your Groq API key for accessing Groq models.
   - `NETLIFY`: Your Netlify API key for deploying and managing web projects.

- API_ENDPOINTS
   - `BING`: The Bing API endpoint for web searching.
   - `GOOGLE`: The Google API endpoint for web searching.
   - `OLLAMA`: The Ollama API endpoint for accessing Local LLMs.
   - `OPENAI`: The OpenAI API endpoint for accessing OpenAI models.

Make sure to keep your API keys secure and do not share them publicly. For setting up the Bing and Google search API keys, follow the instructions in the [search engine setup](docs/Installation/search_engine.md)

## Contributing

We welcome contributions to enhance Devika's capabilities and improve its performance. To contribute, please see the [`CONTRIBUTING.md`](CONTRIBUTING.md) file for steps.

## Help and Support

If you have any questions, feedback, or suggestions, please feel free to reach out to us. you can raise an issue in the [issue tracker](https://github.com/stitionai/devika/issues) or join the [discussions](https://github.com/stitionai/devika/discussions) for general discussions.

We also have a Discord server for the Devika community, where you can connect with other users, share your experiences, ask questions, and collaborate on the project. To join the Devika community Discord server, [click here](https://discord.gg/CYRp43878y).

## License

Devika is released under the [MIT License](https://opensource.org/licenses/MIT). See the `LICENSE` file for more information.

## Star History

<div align="center">
<a href="https://star-history.com/#stitionai/devika&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=stitionai/devika&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=stitionai/devika&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=stitionai/devika&type=Date" />
 </picture>
</a>
</div>

---

We hope you find Devika to be a valuable tool in your software development journey. If you have any questions, feedback, or suggestions, please don't hesitate to reach out. Happy coding with Devika!