#utils.py
def format_conversation(conversation):
    formatted = ""
    for turn, (agent, message) in enumerate(conversation, 1):
        formatted += f"Turn {turn} - {agent}: {message}\n\n"
    return formatted