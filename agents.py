#agents.py
from crewai import Agent
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY,GOOGLE_CREDENTIALS,MAX_TOKENS

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


gemini_agent = Agent(
    role='Gemini',
    goal='Engage in an insightful discussion and provide unique perspectives.',
    backstory="You are Gemini, an AI model developed by Google.",
    verbose=True,
    allow_delegation=False,
    llm_config={
        "provider": "google",
        "model": "gemini-1.5-flash",  # gemini-1.5-flash, gemini-pro
        "credentials": GOOGLE_CREDENTIALS,
        "temperature": 0.7,
        "max_tokens": MAX_TOKENS
    }
)


# Dictionary to easily access agents by name
agent_dict = {
    "chatgpt": chatgpt_agent,
    "claude": claude_agent,
    "gemini": gemini_agent
}