# mcp_server_for_claudes_toolbox
## Author: Claude 3.7 Sonnet, Kyle Rose
## Version: 0.1.0a
A server application that exposes Claude's Toolbox utility programs via the Model Context Protocol (MCP), making them accessible to AI assistants like Claude through different interfaces (Claude Code, Claude Desktop, Copilot, etc.).

## Features
Current tools include:
- **test_generator**: Creates unittest test files from JSON specifications.
- **documentation_generator**: Generates markdown documentation from Python source code.
- **lint_a_python_codebase**: Fixes common linting issues in Python files like blank lines, trailing spaces, and newlines.
- **run_tests_and_save_their_results**: Runs unit tests, type checking, and linting for Python projects, and saves the results as JSON and Markdown files.
- **codebase_search**: Searches code with pattern matching.

## Requirements
- WSL2, Linux. Window support is forthcoming.
- Python 3.12+
- mcp # for MCP server
- aiofile # for async file operations
- anthropic # for LLM API access from Anthropic
- coverage # for test coverage
- duckdb # for cross-platform database operations
- flask # for web framework
- flake8 # for linting
- httpx # for async HTTP requests
- jinja2 # for templating
- mcp # for Claude tool server API
- multiformats # for CID creation
- mypy # for type checking
- numpy # for numerical operations
- openai # for LLM api access from OpenAI
- psutil # for system and process utilities
- pydantic # for data validation and settings management
- pytest # for testing
- pyyaml # for YAML parsing
- tqdm # for progress bars




## Installation

1. Clone this repository:

```bash
git clone [repository-url]
```

2. Run the installation script:

For Linux/MacOS:
```bash
cd claudes_toolbox
bash ./install_server.sh
```

For Windows:
```batch
cd claudes_toolbox
.\install_server.bat
```

3. Copy-paste the respective config code into the relevant MCP config file. 
For Claude Desktop, this is typically located at `C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json`.
Note: This has been tested with Claude Desktop for Windows.


### Server hosted on WSL:
run_wsl.config
```json
"claudes-toolbox": {
    "command": "wsl",
    "args": [
    "bash",
    "-c",
    "source ~/.bashrc && ~/claudes_toolbox/mcp_server_for_claudes_toolbox/start_claudes_toolbox_server.sh --called-with-wsl"
    ]
}
```

### Server hosted on Linux/MacOS:
run_linux.config
```json
"claudes-toolbox": {
  "command": "bash",
  "args": [
    "-c",
    "source ~/.bashrc || source ~/.bash_profile || source ~/.zshrc; ~/claudes_toolbox/start_server.sh"
  ]
}
```

### Server hosted on Windows:

4. Git-clone the other repositories into the `claude_toolbox` directory:

```bash
git clone https://github.com/the-ride-never-ends/documentation_generator claude_toolbox
git clone https://github.com/the-ride-never-ends/test_generator claude_toolbox
git clone https://github.com/the-ride-never-ends/run_tests_and_save_their_results claude_toolbox
git clone https://github.com/the-ride-never-ends/lint_a_python_codebase claude_toolbox
git clone https://github.com/the-ride-never-ends/codebase_search claude_toolbox
```

Note: Each tool is a standalone CLI utility and are currently setup to use their own virtual environments. 


The server will automatically activate the appropriate virtual environment for each tool when called.


 Unlike the MCP server, the tools use `pip` instead of `nv` for installation.

## Usage

The server works by:
- Running tools through subprocess calls to the command line
- Using a wrapper function that activates virtual environments
- Exposing each tool with appropriate parameters via the MCP protocol
- Running asynchronously with FastAPI/Uvicorn under the hood

To start the server:

```bash
./start.sh
```

### Available Tools

The server exposes these tools to AI assistants:

#### test_generator
```
Generates test files based on JSON input
```

#### documentation_generator
```
Generates documentation from Python source code
```

#### lint_a_python_codebase
```
Fixes common linting issues in Python codebases
```

#### run_tests_and_save_their_results
```
Runs tests, type checking, and linting for Python projects
```

#### codebase_search
```
Searches codebases for specific patterns with structured output
```

## Examples

Using the test generator via MCP:

```python
# Example from an AI assistant calling the test generator
result = test_generator(
    name="string_validation",
    description="Tests for string validation functions",
    test_parameter_json="test_params.json",
    output_dir="tests",
    harness="pytest"
)
```

Running the documentation generator:

```python
# Example from an AI assistant calling the documentation generator
result = documentation_generator(
    input_path="my_project/src",
    output_path="docs",
    docstring_style="google",
    inheritance=True
)
```

## Configuration

The server can be configured through the `configs.yaml` file:

```yaml
verbose: True
log_level: 10  # DEBUG level
host: '0.0.0.0'
port: 8000
reload: True
```

## Directory Structure

```dir
mcp_server_for_claudes_toolbox/
├── docs/               # Documentation files
├── tests/              # Test files and test cases
├── utils/              # Utility scripts
├── data/               # Data files used by the program (if any)
├── app.py              # MCP server application
├── configs.py          # Configurations singleton for the program
├── logger.py           # Logger singleton for the program
├── TODO.md             # Todo list 
├── CHANGELOG.md        # Changelog list
├── claude.md           # Instructions to Claude in Claude Code API
├── requirements.txt    # 3rd-party library requirements
├── install.sh          # Set-up venv and install requirements
├── start.sh            # Script to start the server
└── README.md           # This file
```

## License

MIT