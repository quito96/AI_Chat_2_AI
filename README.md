# AI Chat 2 AI

## Project Overview

AI Chat 2 AI is an innovative project that facilitates a structured conversation between two AI models (ChatGPT and Claude) on a given topic. The project uses the CrewAI framework to manage the interaction between the AI agents and generate a comprehensive summary of the discussion.

## Features

- Dynamic conversation between two AI models (ChatGPT and Claude)
- User-defined discussion topics
- Structured turn-based dialogue
- Comprehensive summary generation
- Configurable number of conversation turns

## Components

1. **main.py**: The main script that orchestrates the conversation and summary generation.
2. **agents.py**: Defines the AI agents (ChatGPT and Claude) using the CrewAI framework.
3. **tasks.py**: Contains task definitions for the discussion and summary generation.
4. **utils.py**: Utility functions for formatting the conversation.
5. **config.py**: Configuration settings including API keys and conversation parameters.

## How It Works

1. The user inputs a discussion topic.
2. The program initiates a turn-based conversation between ChatGPT and Claude on the given topic.
3. Each AI agent responds to the other's previous statement, addressing them by name.
4. After the specified number of turns, the conversation is concluded.
5. A summary of the entire discussion is generated, highlighting key points and conclusions.

## Key Features

- **Dynamic Interaction**: The AI agents engage in a back-and-forth dialogue, building upon each other's responses.
- **Personalized Responses**: Agents address each other by name, creating a more natural conversation flow.
- **Structured Summary**: The final summary provides a concise overview of the main points discussed and the conclusions reached.
- **Flexibility**: The system can handle various discussion topics, making it versatile for different use cases.

## Configuration

- The number of conversation turns can be adjusted in the `config.py` file.
- API keys for OpenAI (ChatGPT) and Anthropic (Claude) should be set in a `.env` file.

## Requirements

- Python 3.x
- CrewAI library
- OpenAI API key
- Anthropic API key

## Usage

1. Set up the required API keys in a `.env` file.
2. Run `main.py`.
3. Enter a discussion topic when prompted.
4. The program will generate the conversation and summary automatically.

## Future Improvements

- Implement more diverse AI models for multi-agent discussions.
- Add support for saving conversations and summaries to files.
- Develop a user interface for easier interaction and visualization of the conversation.

This project demonstrates the potential of AI-to-AI interactions in generating insightful discussions and summaries on various topics, showcasing the capabilities of large language models in structured dialogue scenarios.