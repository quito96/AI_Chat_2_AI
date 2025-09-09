# agent_metadata.py - Erweiterte Agent-Metadaten für Transparenz
from typing import Dict, Any, List
from agents import agent_dict
from config import MAX_TOKENS


def get_agent_metadata(agent_name: str) -> Dict[str, Any]:
    """
    Extrahiert detaillierte Metadaten eines Agents basierend auf agents.py Konfiguration
    
    Args:
        agent_name: Name des Agents (chatgpt, claude, granite, gemini)
        
    Returns:
        Dictionary mit allen relevanten Agent-Metadaten
    """
    if agent_name not in agent_dict:
        return {"error": f"Agent {agent_name} nicht gefunden"}
    
    agent = agent_dict[agent_name]
    
    # Basis-Metadaten
    metadata = {
        "name": agent_name,
        "role": agent.role,
        "goal": agent.goal,
        "backstory": agent.backstory,
        "provider": "Unbekannt",
        "model": "Unbekannt", 
        "version": "Unbekannt",
        "temperature": "Standard",
        "max_tokens": MAX_TOKENS,
        "base_url": None
    }
    
    # Hardcoded Konfiguration basierend auf agents.py
    if agent_name == "granite":
        metadata.update({
            "provider": "Ollama (Local)",
            "model": "granite3-dense:8b",
            "version": "Granite 3 Dense 8B",
            "base_url": "http://localhost:11434",
            "temperature": "Standard",
            "max_tokens": "Unbegrenzt (lokal)"
        })
    
    elif agent_name == "chatgpt":
        metadata.update({
            "provider": "OpenAI",
            "model": "gpt-5", 
            "version": "GPT-5 (Latest)",
            "temperature": 0.7,
            "max_tokens": MAX_TOKENS
        })
    
    elif agent_name == "claude":
        metadata.update({
            "provider": "Anthropic",
            "model": "claude-opus-4-20250514",
            "version": "Claude Opus 4 (2025-05-14)",
            "temperature": 0.7,
            "max_tokens": MAX_TOKENS
        })
    
    elif agent_name == "gemini":
        metadata.update({
            "provider": "Google",
            "model": "gemini-2.5-flash",
            "version": "Gemini 2.5 Flash",
            "temperature": 0.7,
            "max_tokens": MAX_TOKENS
        })
    
    return metadata


def get_all_agents_metadata(selected_models: List[str]) -> List[Dict[str, Any]]:
    """
    Holt Metadaten für alle ausgewählten Agents
    
    Args:
        selected_models: Liste der ausgewählten Modellnamen
        
    Returns:
        Liste mit Metadaten für alle Agents
    """
    return [get_agent_metadata(model) for model in selected_models]


def format_agents_for_summary(selected_models: List[str]) -> str:
    """
    Formatiert Agent-Informationen für die Zusammenfassung
    
    Args:
        selected_models: Liste der ausgewählten Modellnamen
        
    Returns:
        Formatierte Teilnehmer-Information für Summary
    """
    agents_metadata = get_all_agents_metadata(selected_models)
    
    participants = []
    for meta in agents_metadata:
        if "error" not in meta:
            participant_info = f"**{meta['role']}** ({meta['provider']} {meta['model']} - {meta['version']})"
            participants.append(participant_info)
    
    return f"**Teilnehmer der Diskussion:**\n" + "\n".join([f"- {p}" for p in participants])


def format_technical_details(selected_models: List[str]) -> str:
    """
    Formatiert technische Details für die Anzeige
    
    Args:
        selected_models: Liste der ausgewählten Modellnamen
        
    Returns:
        Formatierte technische Details
    """
    agents_metadata = get_all_agents_metadata(selected_models)
    
    details = ["**Technische Details:**"]
    for meta in agents_metadata:
        if "error" not in meta:
            detail = f"- **{meta['role']}**: {meta['provider']} | {meta['model']} | Temp: {meta['temperature']} | Max-Tokens: {meta['max_tokens']}"
            details.append(detail)
    
    return "\n".join(details)
