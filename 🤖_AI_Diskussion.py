# app.py - AI Multi-Model Discussion System - Streamlit Interface
import streamlit as st
import time
from datetime import datetime
from typing import List, Dict

# Lokale Imports
from streamlit_utils import (
    StreamlitDiscussionRunner, 
    format_conversation_for_display,
    create_pdf_from_text,
    get_discussion_templates,
    check_api_status,
    save_discussion_to_session,
    load_discussion_history,
    delete_discussion,
    search_discussions,
    get_discussion_statistics,
    backup_discussions
)
from config import AVAILABLE_MODELS, MAX_TURNS, MAX_TOKENS

# Streamlit Konfiguration
st.set_page_config(
    page_title="🤖 AI Diskussion",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Hauptfunktion der Streamlit App"""
    
    # Header
    st.title("🤖 AI Multi-Model Discussion System")
    st.markdown("*Lassen Sie verschiedene KI-Modelle über Ihr Thema diskutieren*")
    
    # Sidebar - Konfiguration
    with st.sidebar:
        st.header("⚙️ Konfiguration")
        
        # API Status
        st.subheader("📡 API Status")
        api_status = check_api_status()
        for model, status in api_status.items():
            status_icon = "🟢" if status else "🔴"
            st.write(f"{status_icon} {model.title()}")
        
        st.divider()
        
        # Modell-Auswahl
        st.subheader("🤖 Modell-Auswahl")
        available_models = [model for model in AVAILABLE_MODELS if api_status.get(model, False)]
        
        if len(available_models) < 2:
            st.error("⚠️ Mindestens 2 Modelle müssen verfügbar sein!")
            st.stop()
        
        selected_models = st.multiselect(
            "Wählen Sie die Diskussionsteilnehmer:",
            available_models,
            default=available_models[:2] if len(available_models) >= 2 else available_models,
            help="Mindestens 2 Modelle erforderlich"
        )
        
        st.divider()
        
        # Erweiterte Einstellungen
        st.subheader("🔧 Erweiterte Einstellungen")
        
        max_turns = st.slider(
            "Anzahl Diskussionsrunden:",
            min_value=1,
            max_value=10,
            value=MAX_TURNS,
            help=f"Standard: {MAX_TURNS}"
        )
        
        stream_mode = st.checkbox(
            "Streaming-Modus",
            value=True,
            help="Zeigt Antworten Wort für Wort an (langsamer)"
        )
        
        show_full_discussion = st.checkbox(
            "Vollständige Diskussion anzeigen",
            value=True,
            help="Zeigt alle Diskussionsrunden an"
        )
    
    # Hauptbereich - Fokussiert auf das Wesentliche
    # Themen-Eingabe
    st.subheader("💭 Diskussionsthema")
    
    # Template-Auswahl
    templates = get_discussion_templates()
    template_choice = st.selectbox(
        "Vordefinierte Themen:",
        ["Eigenes Thema eingeben"] + list(templates.keys()),
        help="Wählen Sie ein Template oder geben Sie ein eigenes Thema ein"
    )
    
    if template_choice == "Eigenes Thema eingeben":
        topic = st.text_area(
            "Ihr Diskussionsthema:",
            placeholder="Geben Sie hier Ihr Diskussionsthema ein...",
            height=100
        )
    else:
        topic = st.text_area(
            "Diskussionsthema (bearbeitbar):",
            value=templates[template_choice],
            height=100
        )
    
    # Start Button - zentriert und prominent
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_discussion = st.button(
            "🚀 Diskussion starten",
            type="primary",
            disabled=not topic or len(selected_models) < 2,
            use_container_width=True
        )
    
    # Diskussion ausführen
    if start_discussion:
        if not topic.strip():
            st.error("Bitte geben Sie ein Diskussionsthema ein!")
            return
        
        if len(selected_models) < 2:
            st.error("Bitte wählen Sie mindestens zwei Modelle aus!")
            return
        
        # Session State für aktuelle Diskussion
        st.session_state.current_discussion = {
            'topic': topic,
            'models': selected_models,
            'timestamp': datetime.now().isoformat()
        }
        
        # Diskussion durchführen
        run_discussion(topic, selected_models, max_turns, stream_mode, show_full_discussion)
    
    # Geladene Diskussion anzeigen
    if 'loaded_discussion' in st.session_state:
        display_loaded_discussion(st.session_state.loaded_discussion, show_full_discussion)
        if st.button("❌ Geladene Diskussion schließen"):
            del st.session_state.loaded_discussion
            st.rerun()


def run_discussion(topic: str, selected_models: List[str], max_turns: int, stream_mode: bool, show_full: bool):
    """Führt die Diskussion durch"""
    
    st.divider()
    st.subheader("🗣️ Live-Diskussion")
    
    # Container für Progress und Chat
    progress_container = st.container()
    chat_container = st.container()
    
    # Diskussion starten
    runner = StreamlitDiscussionRunner()
    
    with st.spinner("Diskussion wird gestartet..."):
        conversation, summary = runner.run_discussion_with_updates(
            topic, selected_models, progress_container, chat_container, stream_mode, max_turns
        )
    
    if conversation and summary:
        # Diskussion in Session speichern
        save_discussion_to_session(topic, selected_models, conversation, summary)
        
        # Ergebnisse anzeigen
        display_results(topic, conversation, summary, show_full, selected_models, key_prefix="new_")
    else:
        st.error("Diskussion konnte nicht durchgeführt werden.")


def display_results(topic: str, conversation: List[tuple], summary: str, show_full: bool, selected_models: List[str] = None, key_prefix: str = ""):
    """Zeigt Diskussionsergebnisse an"""
    
    st.divider()
    st.subheader("📋 Ergebnisse")
    
    # Technische Details anzeigen
    if selected_models:
        with st.expander("🔧 Technische Details der verwendeten Modelle"):
            from agent_metadata import format_technical_details
            tech_details = format_technical_details(selected_models)
            st.markdown(tech_details)
    
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3 = st.tabs(["📄 Zusammenfassung", "💬 Diskussion", "📥 Export"])
    
    with tab1:
        st.subheader("Zusammenfassung")
        st.markdown(summary)
    
    with tab2:
        st.subheader("Diskussionsverlauf")
        if show_full:
            for i, (agent, message) in enumerate(conversation, 1):
                with st.expander(f"Turn {i} - {agent}", expanded=i <= 2):
                    st.markdown(message)
        else:
            # Nur erste und letzte Nachrichten
            if len(conversation) > 2:
                with st.expander(f"Eröffnung - {conversation[0][0]}", expanded=True):
                    st.markdown(conversation[0][1])
                
                st.info(f"... {len(conversation)-2} weitere Nachrichten ...")
                
                with st.expander(f"Abschluss - {conversation[-1][0]}", expanded=True):
                    st.markdown(conversation[-1][1])
            else:
                for i, (agent, message) in enumerate(conversation, 1):
                    with st.expander(f"Turn {i} - {agent}", expanded=True):
                        st.markdown(message)
    
    with tab3:
        st.subheader("Export-Optionen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown Export
            md_content = format_conversation_for_display(conversation, show_full)
            md_content += f"\n\n## Zusammenfassung\n\n{summary}"
            
            st.download_button(
                label="📄 Als Markdown herunterladen",
                data=md_content,
                file_name=f"diskussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key=f"{key_prefix}download_md"
            )
        
        with col2:
            # PDF Export
            pdf_content = md_content.replace('#', '').replace('*', '')  # Einfache Bereinigung
            pdf_bytes = create_pdf_from_text(pdf_content, f"Diskussion: {topic}")
            
            st.download_button(
                label="📑 Als PDF herunterladen",
                data=pdf_bytes,
                file_name=f"diskussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key=f"{key_prefix}download_pdf"
            )


def display_loaded_discussion(discussion: Dict, show_full: bool):
    """Zeigt eine geladene Diskussion an"""
    
    st.divider()
    st.subheader("📚 Geladene Diskussion")
    
    st.info(f"**Thema:** {discussion['topic']}")
    st.info(f"**Modelle:** {', '.join(discussion['models'])}")
    st.info(f"**Datum:** {discussion['timestamp'][:19]}")
    
    display_results(
        discussion['topic'], 
        discussion['conversation'], 
        discussion['summary'], 
        show_full,
        discussion['models'],
        key_prefix="loaded_"
    )


if __name__ == "__main__":
    main()

