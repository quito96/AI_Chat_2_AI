# AI Multi-Model Discussion System

## Overview
This project implements an AI-driven discussion system that allows multiple language models to engage in a conversation on a given topic. It supports the use of OpenAI's ChatGPT, Anthropic's Claude, and Google's Gemini (optional) to create dynamic, multi-perspective discussions.

## Features
- Supports multiple AI models: ChatGPT, Claude, and Gemini (optional)
- User-defined discussion topics
- Configurable number of conversation turns
- Automatic summary generation of the discussion
- Flexible model selection for each discussion

## Prerequisites
- Python 3.11+ (automatically managed by uv)
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Anthropic API key
- Google Gemini credentials (optional)

## Installation
1. Install uv (if not already installed):

```bash
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Clone the repository:

```bash
git clone https://github.com/quito96/Al_Chat_2_Al.git
cd Al_Chat_2_Al
```

3. Install Python 3.11 and project dependencies:

```bash
uv sync
```

4. Set up environment variables:
Create a `.env` file in the project root and add your API keys:

```txt
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_CREDENTIALS_PATH="path2credendials **.json"
```

5. (Optional) For Google Gemini:
Place your Gemini credentials JSON file in the project directory and update the path in `config.py`.

## Usage
Run the main script using uv:

```bash
uv run python main.py
```

Follow the prompts to enter a discussion topic and select the AI models you want to use for the conversation.

### Available Commands
- Run the main discussion system: `uv run python main.py`
- Check available Anthropic models: `uv run python utils/get_anthropic_models.py`
- Check available OpenAI models: `uv run python utils/get_openai_models.py`

## Project Structure
- `main.py`: Main script to run the discussion system
- `agents.py`: Defines AI agents (ChatGPT, Claude, Gemini, Granite)
- `tasks.py`: Defines discussion and summary tasks
- `utils.py`: Utility functions for formatting conversations
- `config.py`: Configuration settings and API key management
- `pyproject.toml`: Project configuration and dependencies (uv/pip compatible)
- `utils/`: Additional utility scripts for model information
  - `get_anthropic_models.py`: Fetch available Anthropic models
  - `get_openai_models.py`: Fetch available OpenAI models

## Configuration
- Adjust `MAX_TURNS` in `config.py` to change the number of conversation turns (default: 5)
- Modify `MAX_TOKENS` in `config.py` to adjust the maximum length of model responses (default: 2000)
- Update model configurations in `agents.py` to use different AI model versions
- Dependencies are managed in `pyproject.toml`

### Supported AI Models
- **ChatGPT**: OpenAI GPT-4o (configurable)
- **Claude**: Anthropic Claude Opus 4 (configurable) 
- **Gemini**: Google Gemini 1.5 Flash (optional, requires credentials)
- **Granite**: IBM Granite 3 Dense 8B (via Ollama, local)

## Contributing
Contributions to improve the project are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.

## Technical Details
- **Python Version**: 3.11+
- **Package Manager**: uv (fast, modern Python package manager)
- **CrewAI Version**: 0.177.0+ (latest features and improvements)
- **Virtual Environment**: Automatically managed by uv

## Development
To contribute to the project:

```bash
# Install development dependencies
uv sync --dev

# Run with development tools
uv run python main.py
```

## Acknowledgments
- OpenAI for the ChatGPT API
- Anthropic for the Claude API  
- Google for the Gemini API (optional)
- IBM for the Granite model (via Ollama)
- The CrewAI library for agent orchestration
- Astral for the uv package manager
