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
```json
"claudes-toolbox": {
    "command": "cmd.exe",
    "args": [
        "/c",
        "C:\\path\\to\\start_server.bat"
    ]
}
```

4. Git-clone the other repositories into the `claude_toolbox` directory:

```bash
cd claudes_toolbox/tools
git clone https://github.com/the-ride-never-ends/documentation_generator
git clone https://github.com/the-ride-never-ends/test_generator
git clone https://github.com/the-ride-never-ends/run_tests_and_save_their_results
git clone https://github.com/the-ride-never-ends/lint_a_python_codebase
git clone https://github.com/the-ride-never-ends/codebase_search
```

Note: Each tool is a standalone CLI utility and can be setup to use their own virtual environments. 


The server will automatically activate the appropriate virtual environment for each tool when called.


## Usage

Integrated applications like Copilot, Claude Code, and Claude Desktop can call the server using the MCP protocol. The server starts automatically when the given command is executed. 

The server works by:
- Running tools through subprocess calls to the command line
- Using a wrapper function that activates virtual environments
- Exposing each tool with appropriate parameters via the MCP protocol


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