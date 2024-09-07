
#main.py
from crewai import Crew
from agents import chatgpt_agent, claude_agent
from tasks import create_discussion_task, create_summary_task
from utils import format_conversation
from config import MAX_TURNS
from dotenv import load_dotenv

load_dotenv()


def main():
    topic = input("Enter the discussion topic: ")
    print("---\n")
    print(f"# Topic: {topic}")

    conversation = []
    tasks = []

    for turn in range(1, MAX_TURNS + 1):
        chatgpt_task = create_discussion_task(chatgpt_agent, claude_agent, topic, turn)
        if conversation:
            chatgpt_task.context = f"Previous response from Claude: {conversation[-1][1]}"
        tasks.append(chatgpt_task)

        claude_task = create_discussion_task(claude_agent, chatgpt_agent, topic, turn)
        if len(conversation) > 1:
            claude_task.context = f"Previous response from ChatGPT: {conversation[-2][1]}"
        tasks.append(claude_task)

    crew = Crew(
        agents=[chatgpt_agent, claude_agent],
        tasks=tasks,
        verbose=True
    )

    print(f"Starting discussion on topic: {topic}")
    results = crew.kickoff()

    for i, task_output in enumerate(results.tasks_output):  # Geändert von tasks_outputs zu tasks_output
        agent = chatgpt_agent if i % 2 == 0 else claude_agent
        conversation.append((agent.role, task_output))
        print(f"{agent.role}: {task_output}\n")

    formatted_conversation = format_conversation(conversation)

    summary_task = create_summary_task(chatgpt_agent, topic, formatted_conversation)
    summary_crew = Crew(
        agents=[chatgpt_agent],
        tasks=[summary_task],
        verbose=True
    )

    summary_result = summary_crew.kickoff()
    summary = summary_result.tasks_output[0]  # Verwenden Sie tasks_output und nehmen Sie das erste Element
    print("---\n")
    print(f"\n## Summary and Conclusion:\n{summary}")


if __name__ == "__main__":
    main()