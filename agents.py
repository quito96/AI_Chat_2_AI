# agents.py
from crewai import Agent,LLM
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_CREDENTIALS, MAX_TOKENS


### language:python
granite_agent = Agent(
    role='Granite',
    goal='Participate in a constructive dialogue and offer unique perspectives.',
    backstory="You are Granite, an AI assistant created by IBM.",
    verbose=True,
    allow_delegation=False,
    llm=LLM(model="ollama/granite3-dense:8b", base_url="http://localhost:11434")
    )

chatgpt_agent = Agent(
    role='ChatGPT',
    goal='Engage in a thoughtful discussion and provide insightful arguments.',
    backstory="You are ChatGPT, an AI language model developed by OpenAI.",
    verbose=True,
    allow_delegation=False,
    llm_config={
        "provider": "openai",
        "model": "gpt-5", #gpt-4o
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
        "model": "claude-opus-4-20250514",
        "api_key": ANTHROPIC_API_KEY,
        "temperature": 0.7,
        "max_tokens": MAX_TOKENS
    }
)

# Gemini agent - only create if credentials are available
gemini_agent = None
if GOOGLE_CREDENTIALS:
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
    "granite": granite_agent
}

# Add Gemini only if available
if gemini_agent:
    agent_dict["gemini"] = gemini_agent
