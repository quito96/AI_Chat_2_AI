# main.py
from crewai import Crew
from agents import agent_dict
from tasks import create_discussion_task, create_summary_task
from utils import format_conversation
from config import MAX_TURNS, AVAILABLE_MODELS
from dotenv import load_dotenv

load_dotenv()


def main():
    topic = input("Enter the discussion topic: ")

    # choose model
    print("Available models:", ", ".join(AVAILABLE_MODELS))
    selected_models = input("Enter the models you want to use (comma-separated): ").split(',')
    selected_models = [model.strip().lower() for model in selected_models if model.strip().lower() in AVAILABLE_MODELS]

    if len(selected_models) < 2:
        print("Please select at least two models.")
        return

    conversation = []
    tasks = []

    for turn in range(1, MAX_TURNS + 1):
        for i in range(len(selected_models)):
            current_agent = agent_dict[selected_models[i]]
            next_agent = agent_dict[selected_models[(i + 1) % len(selected_models)]]
            tasks.append(create_discussion_task(current_agent, next_agent, topic, turn))

    crew = Crew(
        agents=[agent_dict[model] for model in selected_models],
        tasks=tasks,
        verbose=True
    )

    print(f"Starting discussion on topic: {topic}")
    results = crew.kickoff()

    for i, result in enumerate(results.tasks_output):
        agent = agent_dict[selected_models[i % len(selected_models)]]
        conversation.append((agent.role, result))
        print(f"{agent.role}: {result}\n")

    formatted_conversation = format_conversation(conversation)

    summary_task = create_summary_task(agent_dict[selected_models[0]], topic, formatted_conversation)
    summary_crew = Crew(
        agents=[agent_dict[selected_models[0]]],
        tasks=[summary_task],
        verbose=True
    )

    summary_result = summary_crew.kickoff()
    summary = summary_result.tasks_output[0]

    print("\nSummary and Conclusion:")
    print(summary)


if __name__ == "__main__":
    main()