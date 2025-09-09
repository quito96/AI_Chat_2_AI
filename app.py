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
    page_title="AI Multi-Model Discussion",
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
            value=False,
            help="Zeigt Antworten Wort für Wort an (langsamer)"
        )
        
        show_full_discussion = st.checkbox(
            "Vollständige Diskussion anzeigen",
            value=True,
            help="Zeigt alle Diskussionsrunden an"
        )
    
    # Hauptbereich
    col1, col2 = st.columns([2, 1])
    
    with col1:
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
        
        # Start Button
        start_discussion = st.button(
            "🚀 Diskussion starten",
            type="primary",
            disabled=not topic or len(selected_models) < 2,
            use_container_width=True
        )
    
    with col2:
        # Diskussions-Historie & Management
        st.subheader("📚 Diskussions-Management")
        
        # Tabs für verschiedene Funktionen
        tab1, tab2, tab3 = st.tabs(["📜 Historie", "🔍 Suchen", "📊 Statistiken"])
        
        with tab1:
            history = load_discussion_history()
            
            if history:
                st.write(f"**{len(history)} Diskussionen verfügbar**")
                
                # Letzte Diskussionen anzeigen
                for i, entry in enumerate(reversed(history[-5:])):  # Letzte 5
                    # Erweiterte Anzeige mit mehr Informationen
                    topic_preview = entry['topic'][:50] + "..." if len(entry['topic']) > 50 else entry['topic']
                    date_str = entry['timestamp'][:19].replace('T', ' ')
                    models_str = ', '.join(entry['models'])
                    
                    with st.expander(f"💬 {topic_preview}", expanded=False):
                        st.write(f"**📅 Datum:** {date_str}")
                        st.write(f"**🤖 Modelle:** {models_str}")
                        st.write(f"**🔢 DB-ID:** {entry.get('db_id', 'Nicht verfügbar')}")
                        
                        # Buttons in separaten Spalten
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            if st.button(f"📖 Laden", key=f"load_hist_{i}", use_container_width=True):
                                st.session_state.loaded_discussion = entry
                                st.success(f"Diskussion '{entry['topic'][:30]}...' geladen!")
                                st.rerun()
                        
                        with col2:
                            if st.button(f"🗑️ Löschen", key=f"delete_hist_{i}", type="secondary", use_container_width=True):
                                db_id = entry.get('db_id', 0)
                                if db_id and delete_discussion(db_id):
                                    st.success("Diskussion gelöscht!")
                                    st.rerun()
                                else:
                                    st.error("Fehler beim Löschen!")
                        
                        with col3:
                            # Info-Button für Details
                            if st.button(f"ℹ️ Info", key=f"info_hist_{i}", use_container_width=True):
                                st.info(f"**Diskussion Details:**\n- Turns: {len(entry.get('conversation', []))}\n- Zusammenfassung: {entry.get('summary', 'Keine')[:100]}...")
            else:
                st.info("Noch keine Diskussionen gespeichert")
        
        with tab2:
            # Suchfunktion
            search_term = st.text_input("🔍 Diskussionen durchsuchen:", placeholder="Suchbegriff eingeben...")
            
            if search_term:
                search_results = search_discussions(search_term)
                
                if search_results:
                    st.write(f"**{len(search_results)} Ergebnisse gefunden:**")
                    
                    for i, result in enumerate(search_results[:3]):  # Top 3 Ergebnisse
                        with st.expander(f"🔍 {result['topic'][:40]}..."):
                            st.write(f"**📅 Datum:** {result['timestamp'][:19].replace('T', ' ')}")
                            st.write(f"**🤖 Modelle:** {', '.join(result['models'])}")
                            st.write(f"**🔢 DB-ID:** {result['id']}")
                            
                            # Buttons für Suchresultate
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                if st.button(f"📖 Laden", key=f"search_load_{i}", use_container_width=True):
                                    # Vollständige Diskussion aus DB laden
                                    from database_manager import get_database
                                    db = get_database()
                                    full_discussion = db.load_discussion_with_messages(result['id'])
                                    if full_discussion:
                                        st.session_state.loaded_discussion = full_discussion
                                        st.success("Diskussion geladen!")
                                        st.rerun()
                            
                            with col2:
                                if st.button(f"🗑️ Löschen", key=f"search_delete_{i}", type="secondary", use_container_width=True):
                                    if delete_discussion(result['id']):
                                        st.success("Diskussion gelöscht!")
                                        st.rerun()
                                    else:
                                        st.error("Fehler beim Löschen!")
                else:
                    st.info("Keine Ergebnisse gefunden.")
        
        with tab3:
            # Statistiken
            try:
                stats = get_discussion_statistics()
                
                st.metric("Gesamt Diskussionen", stats['total_discussions'])
                st.metric("Gesamt Nachrichten", stats['total_messages'])
                
                if stats['latest_discussion']:
                    st.write(f"**Neueste Diskussion:**")
                    st.write(f"- {stats['latest_discussion']['topic'][:50]}...")
                    st.write(f"- {stats['latest_discussion']['timestamp'][:19]}")
                
                # Backup-Funktion
                if st.button("💾 Backup erstellen"):
                    backup_path = f"discussions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    if backup_discussions(backup_path):
                        st.success(f"Backup erstellt: {backup_path}")
                    else:
                        st.error("Fehler beim Backup!")
                        
            except Exception as e:
                st.error(f"Fehler beim Laden der Statistiken: {e}")
    
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
        display_results(topic, conversation, summary, show_full)
    else:
        st.error("Diskussion konnte nicht durchgeführt werden.")


def display_results(topic: str, conversation: List[tuple], summary: str, show_full: bool):
    """Zeigt Diskussionsergebnisse an"""
    
    st.divider()
    st.subheader("📋 Ergebnisse")
    
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
                mime="text/markdown"
            )
        
        with col2:
            # PDF Export
            pdf_content = md_content.replace('#', '').replace('*', '')  # Einfache Bereinigung
            pdf_bytes = create_pdf_from_text(pdf_content, f"Diskussion: {topic}")
            
            st.download_button(
                label="📑 Als PDF herunterladen",
                data=pdf_bytes,
                file_name=f"diskussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
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
        show_full
    )


if __name__ == "__main__":
    main()

