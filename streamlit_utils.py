# streamlit_utils.py
import streamlit as st
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os

from crewai import Crew
from agents import agent_dict
from tasks import create_discussion_task, create_summary_task
from utils import format_conversation
from config import MAX_TURNS, AVAILABLE_MODELS


class StreamlitDiscussionRunner:
    """Streamlit-spezifische Wrapper für Diskussionen"""
    
    def __init__(self):
        self.current_crew = None
        self.conversation = []
        self.is_running = False
        
    def run_discussion_with_updates(
        self, 
        topic: str, 
        selected_models: List[str], 
        progress_container,
        chat_container,
        stream_mode: bool = False,
        max_turns: int = MAX_TURNS
    ):
        """Führt Diskussion mit Live-Updates durch"""
        
        if len(selected_models) < 2:
            st.error("Bitte wählen Sie mindestens zwei Modelle aus.")
            return None, None
            
        self.conversation = []
        self.is_running = True
        
        # Progress Setup
        progress_bar = progress_container.progress(0)
        status_text = progress_container.empty()
        
        # Tasks erstellen
        tasks = []
        total_tasks = max_turns * len(selected_models)
        
        try:
            for turn in range(1, max_turns + 1):
                for i in range(len(selected_models)):
                    current_agent = agent_dict[selected_models[i]]
                    next_agent = agent_dict[selected_models[(i + 1) % len(selected_models)]]
                    tasks.append(create_discussion_task(current_agent, next_agent, topic, turn))
            
            # Crew erstellen
            crew = Crew(
                agents=[agent_dict[model] for model in selected_models],
                tasks=tasks,
                verbose=False  # Reduziert Output für Streamlit
            )
            
            status_text.text("🚀 Diskussion gestartet...")
            
            # Diskussion ausführen
            results = crew.kickoff()
            
            # Ergebnisse verarbeiten
            for i, result in enumerate(results.tasks_output):
                agent = agent_dict[selected_models[i % len(selected_models)]]
                self.conversation.append((agent.role, str(result)))
                
                # Progress Update
                progress = (i + 1) / len(results.tasks_output)
                progress_bar.progress(progress)
                current_turn = (i // len(selected_models)) + 1
                status_text.text(f"💬 Turn {current_turn}/{max_turns}: {agent.role} antwortet... ({i + 1}/{len(results.tasks_output)})")
                
                # Chat Update
                if stream_mode:
                    self._display_message_streaming(chat_container, agent.role, str(result))
                else:
                    self._display_message_block(chat_container, agent.role, str(result))
                
                time.sleep(0.1)  # Kurze Pause für UI-Update
            
            # Zusammenfassung erstellen
            status_text.text("📋 Zusammenfassung wird erstellt...")
            formatted_conversation = format_conversation(self.conversation)
            
            summary_task = create_summary_task(agent_dict[selected_models[0]], topic, formatted_conversation)
            summary_crew = Crew(
                agents=[agent_dict[selected_models[0]]],
                tasks=[summary_task],
                verbose=False
            )
            
            summary_result = summary_crew.kickoff()
            summary = str(summary_result.tasks_output[0])
            
            progress_bar.progress(1.0)
            status_text.text("✅ Diskussion abgeschlossen!")
            
            self.is_running = False
            return self.conversation, summary
            
        except Exception as e:
            st.error(f"Fehler während der Diskussion: {str(e)}")
            self.is_running = False
            return None, None
    
    def _display_message_streaming(self, container, agent: str, message: str):
        """Zeigt Nachricht mit Streaming-Effekt"""
        with container.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.write(self._get_agent_avatar(agent))
            with col2:
                st.write(f"**{agent}:**")
                message_placeholder = st.empty()
                
                # Streaming-Effekt
                words = message.split()
                displayed_text = ""
                for i, word in enumerate(words):
                    displayed_text += word + " "
                    message_placeholder.markdown(displayed_text)
                    if i % 5 == 0:  # Update alle 5 Wörter
                        time.sleep(0.05)
    
    def _display_message_block(self, container, agent: str, message: str):
        """Zeigt Nachricht als Block"""
        with container.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.write(self._get_agent_avatar(agent))
            with col2:
                st.write(f"**{agent}:**")
                st.markdown(message)
            st.divider()
    
    def _get_agent_avatar(self, agent: str) -> str:
        """Gibt Avatar-Emoji für Agent zurück"""
        avatars = {
            "ChatGPT": "🤖",
            "Claude": "🧠", 
            "Gemini": "💎",
            "Granite": "🗿"
        }
        return avatars.get(agent, "🤔")


def format_conversation_for_display(conversation: List[tuple], show_full: bool = True) -> str:
    """Formatiert Konversation für Anzeige"""
    if not conversation:
        return "Keine Diskussion verfügbar."
    
    formatted = "# AI Diskussion\n\n"
    
    if show_full:
        for i, (agent, message) in enumerate(conversation, 1):
            formatted += f"## Turn {i} - {agent}\n\n"
            formatted += f"{message}\n\n"
            formatted += "---\n\n"
    else:
        # Nur erste und letzte Nachrichten
        if len(conversation) > 2:
            formatted += f"## {conversation[0][0]} (Eröffnung)\n\n"
            formatted += f"{conversation[0][1]}\n\n"
            formatted += "---\n\n"
            formatted += f"## {conversation[-1][0]} (Abschluss)\n\n" 
            formatted += f"{conversation[-1][1]}\n\n"
        else:
            for agent, message in conversation:
                formatted += f"## {agent}\n\n{message}\n\n---\n\n"
    
    return formatted


def create_pdf_from_text(text: str, title: str = "AI Diskussion") -> bytes:
    """Erstellt PDF aus Text"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Text in Paragraphen aufteilen
    paragraphs = text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            if para.startswith('#'):
                # Überschrift
                clean_para = para.replace('#', '').strip()
                story.append(Paragraph(clean_para, styles['Heading2']))
            else:
                # Normaler Text
                story.append(Paragraph(para, styles['Normal']))
            story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def get_discussion_templates() -> Dict[str, str]:
    """Vordefinierte Diskussionsthemen"""
    return {
        "Künstliche Intelligenz": "Wie wird sich Künstliche Intelligenz in den nächsten 10 Jahren entwickeln?",
        "Klimawandel": "Welche Maßnahmen sind am effektivsten im Kampf gegen den Klimawandel?",
        "Digitalisierung": "Wie verändert die Digitalisierung unsere Arbeitswelt?",
        "Nachhaltigkeit": "Wie können Unternehmen nachhaltiger werden?",
        "Bildung": "Wie sollte sich das Bildungssystem für die Zukunft entwickeln?",
        "Gesundheitswesen": "Welche Innovationen braucht das Gesundheitswesen?",
        "Ethik in der Technologie": "Welche ethischen Grenzen sollte die Technologieentwicklung haben?",
        "Zukunft der Arbeit": "Wie wird sich die Arbeitswelt in der post-digitalen Ära entwickeln?"
    }


def check_api_status() -> Dict[str, bool]:
    """Prüft API-Status der verfügbaren Modelle"""
    status = {}
    for model in AVAILABLE_MODELS:
        try:
            # Vereinfachte Prüfung - könnte erweitert werden
            if model in agent_dict:
                status[model] = True
            else:
                status[model] = False
        except:
            status[model] = False
    
    return status


def save_discussion_to_session(topic: str, models: List[str], conversation: List[tuple], summary: str):
    """Speichert Diskussion in Session State"""
    if 'discussion_history' not in st.session_state:
        st.session_state.discussion_history = []
    
    discussion_entry = {
        'timestamp': datetime.now().isoformat(),
        'topic': topic,
        'models': models,
        'conversation': conversation,
        'summary': summary
    }
    
    st.session_state.discussion_history.append(discussion_entry)


def load_discussion_history() -> List[Dict[str, Any]]:
    """Lädt Diskussionshistorie aus Session State"""
    return st.session_state.get('discussion_history', [])

