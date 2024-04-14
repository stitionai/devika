## Under The Hood

Let's dive deeper into some of the key components and techniques used in Devika:

### AI Planning and Reasoning

Devika employs advanced AI planning and reasoning algorithms to break down high-level objectives into actionable steps. The planning process involves the following stages:

1. **Objective Understanding**: Devika analyzes the given objective or task description to understand the user's intent and requirements.
2. **Context Gathering**: Relevant context is collected from the conversation history, project files, and knowledge base to inform the planning process.
3. **Step Generation**: Based on the objective and context, Devika generates a sequence of high-level steps to accomplish the task.
4. **Refinement and Validation**: The generated steps are refined and validated to ensure their feasibility and alignment with the objective.
5. **Execution**: Devika executes each step in the plan, utilizing various sub-agents and modules as needed.

The reasoning engine constantly evaluates the progress and makes adjustments to the plan based on new information or feedback received during execution.

### Keyword Extraction

To enable focused research and information gathering, Devika employs keyword extraction techniques. The process involves the following steps:

1. **Preprocessing**: The input text (objective, conversation history, or project files) is preprocessed by removing stop words, tokenizing, and normalizing the text.
2. **Keyword Identification**: Devika uses the BERT (Bidirectional Encoder Representations from Transformers) model to identify important keywords and phrases from the preprocessed text. BERT's pre-training on a large corpus allows it to capture semantic relationships and understand the significance of words in the given context.
3. **Keyword Ranking**: The identified keywords are ranked based on their relevance and importance to the task at hand. Techniques like TF-IDF (Term Frequency-Inverse Document Frequency) and TextRank are used to assign scores to each keyword.
4. **Keyword Selection**: The top-ranked keywords are selected as the most relevant and informative for the current context. These keywords are used to guide the research and information gathering process.

By extracting contextually relevant keywords, Devika can focus its research efforts and retrieve pertinent information to assist in the task completion.

### Browser Interaction

Devika incorporates browser interaction capabilities to navigate websites, extract information, and interact with web elements. The browser interaction module leverages the Playwright library to automate web interactions. The process involves the following steps:

1. **Navigation**: Devika uses Playwright to navigate to specific URLs or perform searches based on the keywords or requirements provided.
2. **Element Interaction**: Playwright allows Devika to interact with web elements such as clicking buttons, filling forms, and extracting text from specific elements.
3. **Page Parsing**: Devika parses the HTML structure of the web pages visited to extract relevant information. It uses techniques like CSS selectors and XPath to locate and extract specific data points.
4. **JavaScript Execution**: Playwright enables Devika to execute JavaScript code within the browser context, allowing for dynamic interactions and data retrieval.
5. **Screenshot Capture**: Devika can capture screenshots of the web pages visited, which can be useful for visual reference or debugging purposes.

The browser interaction module empowers Devika to gather information from the web, interact with online resources, and incorporate real-time data into its decision-making and code generation processes.

### Code Writing

Devika's code writing module generates code based on the plan, research findings, and user requirements. The process involves the following steps:

1. **Language Selection**: Devika identifies the programming language specified by the user or infers it based on the project context.
2. **Code Structure Generation**: Based on the plan and language-specific patterns, Devika generates the high-level structure of the code, including classes, functions, and modules.
3. **Code Population**: Devika fills in the code structure with specific logic, algorithms, and data manipulation statements. It leverages the research findings, code snippets from the knowledge base, and its own understanding of programming concepts to generate meaningful code.
4. **Code Formatting**: The generated code is formatted according to the language-specific conventions and best practices to ensure readability and maintainability.
5. **Code Review and Refinement**: Devika reviews the generated code for syntax errors, logical inconsistencies, and potential improvements. It iteratively refines the code based on its own analysis and any feedback provided by the user.

Devika's code writing capabilities enable it to generate functional and efficient code in various programming languages, taking into account the specific requirements and context of each project.