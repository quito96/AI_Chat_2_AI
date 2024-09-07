#agents.py
from crewai import Agent
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY,MAX_TOKENS

chatgpt_agent = Agent(
    role='ChatGPT',
    goal='Engage in a thoughtful discussion and provide insightful arguments.',
    backstory="You are ChatGPT, an AI language model developed by OpenAI.",
    verbose=True,
    allow_delegation=False,
    llm_config={
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": OPENAI_API_KEY,
        "temperature": 0.7,
        "max_tokens": MAX_TOKENS
    }
)

claude_agent = Agent(
    role='Claude',
    goal='Participate in a constructive dialogue and offer unique perspectives.',
    backstory="You are Claude, an AI assistant created by Anthropic.",
    verbose=True,
    allow_delegation=False,
    llm_config={
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20240620",
        "api_key": ANTHROPIC_API_KEY,
        "temperature": 0.7,
        "max_tokens": MAX_TOKENS
    }
)
