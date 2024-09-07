#tasks.ai
from crewai import Task

def create_discussion_task(agent, other_agent, topic, turn):
    return Task(
        description=f"Discuss the topic: {topic}. This is turn {turn} of the conversation. "
                    f"You are {agent.role}. Address {other_agent.role} directly by name in your response. "
                    f"If this is not the first turn, respond to {other_agent.role}'s previous statement. "
                    f"Keep your response concise and to the point. Important: Answer in the topic language.",
        agent=agent,
        expected_output=f"A thoughtful response from {agent.role} to {other_agent.role}, "
                        f"continuing the discussion on the given topic."
    )

def create_summary_task(agent, topic, conversation):
    return Task(
        description=f"Summarize the discussion on '{topic}' and provide a conclusion. "
                    f"Consider the following points:\n"
                    f"1. Summarize the main arguments and insights from both participants.\n"
                    f"2. Identify key agreements and potential differences in viewpoints.\n"
                    f"3. Create a structured summary of the key points.\n"
                    f"4. Formulate a joint conclusion that captures the essence of the discussion.\n"
                    f"5. Keep the summary concise and to the point.\n"
                    f"Here's the conversation: {conversation}",
        agent=agent,
        expected_output="A structured, concise summary of the discussion with a clear, "
                        "joint conclusion. Important: Answer in the language of the discussion topic."
    )