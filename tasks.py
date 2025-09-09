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

def create_summary_task(agent, topic, conversation, participants_info: str = ""):
    return Task(
        description=f"Summarize the discussion on '{topic}' and provide a conclusion. "
                    f"Consider the following points:\n"
                    f"1. Start with the participants information: {participants_info}\n"
                    f"2. Summarize the main arguments and insights from each participant by name.\n"
                    f"3. Identify key agreements and potential differences in viewpoints.\n"
                    f"4. Create a structured summary of the key points.\n"
                    f"5. Formulate a joint conclusion that captures the essence of the discussion.\n"
                    f"6. Keep the summary concise and to the point.\n"
                    f"Here's the conversation: {conversation}",
        agent=agent,
        expected_output="A structured, concise summary of the discussion starting with participant details, "
                        "clearly naming each AI model/participant in the analysis, and ending with a joint conclusion. "
                        "Important: Answer in the language of the discussion topic."
    )