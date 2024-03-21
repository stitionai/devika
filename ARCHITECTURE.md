# Devika Architecture

Devika is an advanced AI software engineer that can understand high-level human instructions, break them down into steps, research relevant information, and write code to achieve a given objective. This document provides a detailed technical overview of Devika's system architecture and how the various components work together.

## Table of Contents

1. [Overview](#overview)
2. [Agent Core](#agent-core)
3. [Agents](#agents)
   - [Planner](#planner)
   - [Researcher](#researcher) 
   - [Coder](#coder)
   - [Action](#action)
   - [Runner](#runner)
   - [Feature](#feature)
   - [Patcher](#patcher)
   - [Reporter](#reporter)
   - [Decision](#decision)
4. [Language Models](#language-models)
5. [Browser Interaction](#browser-interaction) 
6. [Project Management](#project-management)
7. [Agent State Management](#agent-state-management)
8. [Services](#services)
9. [Utilities](#utilities)
10. [Conclusion](#conclusion)

## Overview

At a high level, Devika consists of the following key components:

- **Agent Core**: Orchestrates the overall AI planning, reasoning and execution process. Communicates with various sub-agents.
- **Agents**: Specialized sub-agents that handle specific tasks like planning, research, coding, patching, reporting etc.  
- **Language Models**: Leverages large language models (LLMs) like Claude, GPT-4, GPT-3 for natural language understanding and generation.
- **Browser Interaction**: Enables web browsing, information gathering, and interaction with web elements.
- **Project Management**: Handles organization and persistence of project-related data. 
- **Agent State Management**: Tracks and persists the dynamic state of the AI agent across interactions.
- **Services**: Integrations with external services like GitHub, Netlify for enhanced capabilities.
- **Utilities**: Supporting modules for configuration, logging, vector search, PDF generation etc.

Let's dive into each of these components in more detail.

## Agent Core

The `Agent` class serves as the central engine that drives Devika's AI planning and execution loop. Here's how it works:

1. When a user provides a high-level prompt, the `execute` method is invoked on the Agent. 
2. The prompt is first passed to the Planner agent to generate a step-by-step plan.
3. The Researcher agent then takes this plan and extracts relevant search queries and context.
4. The Agent performs web searches using Bing Search API and crawls the top results. 
5. The raw crawled content is passed through the Formatter agent to extract clean, relevant information.
6. This researched context, along with the step-by-step plan, is fed to the Coder agent to generate code.
7. The generated code is saved to the project directory on disk.
8. If the user interacts further with a follow-up prompt, the `subsequent_execute` method is invoked.
9. The Action agent determines the appropriate action to take based on the user's message (run code, deploy, write tests, add feature, fix bug, write report etc.)
10. The corresponding specialized agent is invoked to perform the action (Runner, Feature, Patcher, Reporter).
11. Results are communicated back to the user and the project files are updated.

Throughout this process, the Agent Core is responsible for:
- Managing conversation history and project-specific context
- Updating agent state and internal monologue 
- Accumulating context keywords across agent prompts
- Emulating the "thinking" process of the AI through timed agent state updates
- Handling special commands through the Decision agent (e.g. git clone, browser interaction session)

## Agents

Devika's cognitive abilities are powered by a collection of specialized sub-agents. Each agent is implemented as a separate Python class. Agents communicate with the underlying LLMs through prompt templates defined in Jinja2 format. Key agents include:

### Planner
- Generates a high-level step-by-step plan based on the user's prompt
- Extracts focus area and provides a summary
- Uses few-shot prompting to provide examples of the expected response format

### Researcher
- Takes the generated plan and extracts relevant search queries 
- Ranks and filters queries based on relevance and specificity
- Prompts the user for additional context if required
- Aims to maximize information gain while minimizing number of searches

### Coder
- Generates code based on the step-by-step plan and researched context
- Segments code into appropriate files and directories
- Includes informative comments and documentation
- Handles a variety of languages and frameworks
- Validates code syntax and style

### Action
- Determines the appropriate action to take based on the user's follow-up prompt
- Maps user intent to a specific action keyword (run, test, deploy, fix, implement, report)
- Provides a human-like confirmation of the action to the user

### Runner
- Executes the written code in a sandboxed environment 
- Handles different OS environments (Mac, Linux, Windows)
- Streams command output to user in real-time
- Gracefully handles errors and exceptions

### Feature
- Implements a new feature based on user's specification
- Modifies existing project files while maintaining code structure and style
- Performs incremental testing to verify feature is working as expected

### Patcher
- Debugs and fixes issues based on user's description or error message
- Analyzes existing code to identify potential root causes
- Suggests and implements fix, with explanation of the changes made

### Reporter
- Generates a comprehensive report summarizing the project
- Includes high-level overview, technical design, setup instructions, API docs etc.
- Formats report in a clean, readable structure with table of contents
- Exports report as a PDF document

### Decision
- Handles special command-like instructions that don't fit other agents
- Maps commands to specific functions (git clone, browser interaction etc.)
- Executes the corresponding function with provided arguments

Each agent follows a common pattern:
1. Prepare a prompt by rendering the Jinja2 template with current context
2. Query the LLM to get a response based on the prompt
3. Validate and parse the LLM's response to extract structured output
4. Perform any additional processing or side-effects (e.g. save to disk)
5. Return the result to the Agent Core for further action

Agents aim to be stateless and idempotent where possible. State and history is managed by the Agent Core and passed into the agents as needed. This allows for a modular, composable design.

## Language Models

Devika's natural language processing capabilities are driven by state-of-the-art LLMs. The `LLM` class provides a unified interface to interact with different language models:

- **Claude** (Anthropic): Claude models like claude-v1.3, claude-instant-v1.0 etc.
- **GPT-4/GPT-3** (OpenAI): Models like gpt-4, gpt-3.5-turbo etc.
- **Self-hosted models** (via [Ollama](https://ollama.com/)): Allows using open-source models in a self-hosted environment

The `LLM` class abstracts out the specifics of each provider's API, allowing agents to interact with the models in a consistent way. It supports:
- Listing available models
- Generating completions based on a prompt
- Tracking and accumulating token usage over time

Choosing the right model for a given use case depends on factors like desired quality, speed, cost etc. The modular design allows swapping out models easily.

## Browser Interaction

Devika can interact with webpages in an automated fashion to gather information and perform actions. This is powered by the `Browser` and `Crawler` classes.

The `Browser` class uses Playwright to provide high-level web automation primitives:
- Spawning a browser instance (Chromium)
- Navigating to a URL
- Querying DOM elements 
- Extracting page content as text, Markdown, PDF etc.
- Taking a screenshot of the page

The `Crawler` class defines an agent that can interact with a webpage based on natural language instructions. It leverages:
- Pre-defined browser actions like scroll, click, type etc.
- A prompt template that provides examples of how to use these actions
- LLM to determine the best action to take based on current page content and objective

The `start_interaction` function sets up a loop where:
1. The current page content and objective is passed to the LLM 
2. The LLM returns the next best action to take (e.g. "CLICK 12" or "TYPE 7 machine learning")
3. The Crawler executes this action on the live page
4. The process repeats from the updated page state

This allows performing a sequence of actions to achieve a higher-level objective (e.g. research a topic, fill out a form, interact with an app etc.)

## Project Management

The `ProjectManager` class is responsible for creating, updating and querying projects and their associated metadata. Key functions include:

- Creating a new project and initializing its directory structure
- Deleting a project and its associated files
- Adding a message to a project's conversation history
- Retrieving messages for a given project
- Getting the latest user/AI message in a conversation
- Listing all projects
- Zipping a project's files for export

Project metadata is persisted in a SQLite database using SQLModel. The `Projects` table stores:
- Project name
- JSON-serialized conversation history

This allows the agent to work on multiple projects simultaneously and retain conversation history across sessions.

## Agent State Management

As the AI agent works on a task, we need to track and display its internal state to the user. The `AgentState` class handles this by providing an interface to:

- Initialize a new agent state 
- Add a state to the current sequence of states for a project
- Update the latest state for a project
- Query the latest state or entire state history for a project
- Mark the agent as active/inactive or task as completed

Agent state includes information like:
- Current step or action being executed
- Internal monologue reflecting the agent's current "thoughts"
- Browser interactions (URL visited, screenshot)
- Terminal interactions (command executed, output)
- Token usage so far

Like projects, agent states are also persisted in the SQLite DB using SQLModel. The `AgentStateModel` table stores:
- Project name
- JSON-serialized list of states

Having a persistent log of agent states is useful for:
- Providing real-time visibility to the user
- Auditing and debugging agent behavior
- Resuming from interruptions or failures

## Services

Devika integrates with external services to augment its capabilities:

- **GitHub**: Performing git operations like clone/pull, listing repos/commits/files etc.
- **Netlify**: Deploying web apps and sites seamlessly

The `GitHub` and `Netlify` classes provide lightweight wrappers around the respective service APIs. 
They handle authentication, making HTTP requests, and parsing responses.

This allows Devika to perform actions like:
- Cloning a repo given a GitHub URL
- Listing a user's GitHub repos 
- Creating a new Netlify site
- Deploying a directory to Netlify 
- Providing the deployed site URL to the user

Integrations are done in a modular way so that new services can be added easily.

## Utilities  

Devika makes use of several utility modules to support its functioning:

- `Config`: Loads and provides access to configuration settings (API keys, folder paths etc.) 
- `Logger`: Sets up logging to console and file, with support for log levels and colors
- `ReadCode`: Recursively reads code files in a directory and converts them into a Markdown format
- `SentenceBERT`: Extracts keywords and semantic information from text using SentenceBERT embeddings
- `Experts`: A collection of domain-specific knowledge bases to assist in certain areas (e.g. webdev, physics, chemistry, math)

The utility modules aim to provide reusable functionality that is used across different parts of the system.

## Conclusion

Devika is a complex system that combines multiple AI and automation techniques to deliver an intelligent programming assistant. Key design principles include:

- Modularity: Breaking down functionality into specialized agents and services
- Flexibility: Supporting different LLMs, services and domains in a pluggable fashion  
- Persistence: Storing project and agent state in a DB to enable pause/resume and auditing
- Transparency: Surfacing agent thought process and interactions to user in real-time

By understanding how the different components work together, we can extend, optimize and scale Devika to take on increasingly sophisticated software engineering tasks. The agent-based architecture provides a strong foundation to build more advanced AI capabilities in the future.
