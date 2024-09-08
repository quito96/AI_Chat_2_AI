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
- Python 3.8+
- OpenAI API key
- Anthropic API key
- Google Gemini credentials (optional)

## Installation
1. Clone the repository:

```bash
git clone https://github.com/quito96/Al_Chat_2_Al.git
cd Al_Chat_2_Al
```

2. Install required packages:

```bash
pip install -r requirements.txt
```
3. Set up environment variables:
Create a `.env` file in the project root and add your API keys:

```txt
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_CREDENTIALS_PATH="path2credendials **.json"
```

4. (Optional) For Google Gemini:
Place your Gemini credentials JSON file in the project directory and update the path in `config.py`.

## Usage
Run the main.py script. 

Follow the prompts to enter a discussion topic and select the AI models you want to use for the conversation.

## Project Structure
- `main.py`: Main script to run the discussion system
- `agents.py`: Defines AI agents (ChatGPT, Claude, Gemini)
- `tasks.py`: Defines discussion and summary tasks
- `utils.py`: Utility functions for formatting conversations
- `config.py`: Configuration settings and API key management

## Configuration
- Adjust `MAX_TURNS` in `config.py` to change the number of conversation turns
- Modify `MAX_TOKENS` in `config.py` to adjust the maximum length of model responses

## Contributing
Contributions to improve the project are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgments
- OpenAI for the ChatGPT API
- Anthropic for the Claude API
- Google for the Gemini API (if implemented)
- The CrewAI library for agent orchestration
