# pages/1_📚_Diskussions_Management.py - Separate Seite für Diskussions-Management
import streamlit as st
from streamlit_utils import (
    load_discussion_history, 
    delete_discussion, 
    search_discussions, 
    get_discussion_statistics,
    backup_discussions
)
from database_manager import get_database

# Seitenkonfiguration
st.set_page_config(
    page_title="Diskussions-Management",
    page_icon="📚",
    layout="wide"
)

def display_loaded_discussion(discussion):
    """Zeigt eine geladene Diskussion formatiert an"""
    st.subheader(f"📖 Geladene Diskussion: {discussion['topic']}")
    
    # Metadaten anzeigen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Datum", discussion['timestamp'][:19].replace('T', ' '))
    with col2:
        st.metric("🤖 Modelle", f"{len(discussion['models'])} Teilnehmer")
    with col3:
        st.metric("💬 Nachrichten", len(discussion.get('conversation', [])))
    
    # Technische Details
    if discussion.get('models'):
        with st.expander("🔧 Technische Details der verwendeten Modelle"):
            from agent_metadata import format_technical_details
            tech_details = format_technical_details(discussion['models'])
            st.markdown(tech_details)
    
    # Diskussionsverlauf
    with st.expander("💬 Vollständiger Diskussionsverlauf", expanded=True):
        for i, (agent, message) in enumerate(discussion.get('conversation', [])):
            with st.container():
                st.markdown(f"### Turn {i+1} - {agent}")
                st.markdown(message)
                st.divider()
    
    # Zusammenfassung
    st.subheader("📋 Zusammenfassung")
    st.markdown(discussion.get('summary', 'Keine Zusammenfassung verfügbar'))
    
    # Export-Optionen
    st.subheader("📥 Export")
    col1, col2 = st.columns(2)
    
    with col1:
        # Markdown Export
        markdown_content = f"""# {discussion['topic']}

**Datum:** {discussion['timestamp'][:19].replace('T', ' ')}
**Modelle:** {', '.join(discussion['models'])}

## Diskussionsverlauf

"""
        for i, (agent, message) in enumerate(discussion.get('conversation', [])):
            markdown_content += f"### Turn {i+1} - {agent}\n\n{message}\n\n"
        
        markdown_content += f"## Zusammenfassung\n\n{discussion.get('summary', 'Keine Zusammenfassung verfügbar')}"
        
        st.download_button(
            label="📄 Als Markdown herunterladen",
            data=markdown_content,
            file_name=f"diskussion_{discussion['topic'][:30]}.md",
            mime="text/markdown"
        )
    
    with col2:
        # PDF wäre hier möglich, aber erfordert zusätzliche Bibliotheken
        st.info("📄 PDF-Export: Verwenden Sie den Markdown-Export und konvertieren Sie ihn mit einem Online-Tool zu PDF.")


def main():
    """Hauptfunktion der Diskussions-Management Seite"""
    
    st.title("📚 Diskussions-Management")
    st.markdown("Verwalten Sie Ihre gespeicherten AI-Diskussionen")
    
    # Seitenleiste für Navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        page_selection = st.radio(
            "Wählen Sie einen Bereich:",
            ["📜 Historie", "🔍 Suchen", "📊 Statistiken", "💾 Backup"],
            index=0
        )
    
    # Geladene Diskussion anzeigen (falls vorhanden)
    if 'loaded_discussion' in st.session_state:
        display_loaded_discussion(st.session_state.loaded_discussion)
        
        if st.button("🔙 Zurück zur Übersicht"):
            del st.session_state.loaded_discussion
            st.rerun()
        
        st.divider()
    
    # Hauptinhalt basierend auf Auswahl
    if page_selection == "📜 Historie":
        show_history_section()
    elif page_selection == "🔍 Suchen":
        show_search_section()
    elif page_selection == "📊 Statistiken":
        show_statistics_section()
    elif page_selection == "💾 Backup":
        show_backup_section()


def show_history_section():
    """Zeigt den Historie-Bereich"""
    st.header("📜 Diskussions-Historie")
    
    history = load_discussion_history()
    
    if history:
        st.success(f"**{len(history)} Diskussionen verfügbar**")
        
        # Paginierung für große Listen
        items_per_page = 10
        total_pages = (len(history) + items_per_page - 1) // items_per_page
        
        if total_pages > 1:
            page = st.selectbox("📄 Seite auswählen:", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(history))
            page_history = list(reversed(history))[start_idx:end_idx]
        else:
            page_history = list(reversed(history))
        
        # Diskussionen anzeigen
        for i, entry in enumerate(page_history):
            # Erweiterte Anzeige mit mehr Informationen
            topic_preview = entry['topic'][:60] + "..." if len(entry['topic']) > 60 else entry['topic']
            date_str = entry['timestamp'][:19].replace('T', ' ')
            models_str = ', '.join(entry['models'])
            
            with st.expander(f"💬 {topic_preview}", expanded=False):
                # Informationen in Spalten
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**📅 Datum:** {date_str}")
                    st.write(f"**🤖 Modelle:** {models_str}")
                    st.write(f"**🔢 DB-ID:** {entry.get('db_id', 'Nicht verfügbar')}")
                    st.write(f"**💬 Nachrichten:** {len(entry.get('conversation', []))}")
                
                with col2:
                    # Zusammenfassung Preview
                    summary_preview = entry.get('summary', 'Keine')[:150]
                    if len(entry.get('summary', '')) > 150:
                        summary_preview += "..."
                    st.write(f"**📝 Zusammenfassung:**")
                    st.caption(summary_preview)
                
                # Action Buttons
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    if st.button(f"📖 Vollständig anzeigen", key=f"load_hist_{i}", use_container_width=True):
                        st.session_state.loaded_discussion = entry
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
                    # Info-Button mit verbesserter Darstellung
                    if st.button(f"ℹ️ Details", key=f"info_hist_{i}", use_container_width=True):
                        show_discussion_details(entry)
                
                with col4:
                    # Schneller Markdown-Download
                    if st.button(f"📄 Export", key=f"export_hist_{i}", use_container_width=True):
                        create_markdown_download(entry)
    else:
        st.info("📝 Noch keine Diskussionen gespeichert")
        st.markdown("Starten Sie eine neue Diskussion auf der Hauptseite!")


def show_search_section():
    """Zeigt den Such-Bereich"""
    st.header("🔍 Diskussionen suchen")
    
    search_term = st.text_input(
        "🔍 Suchbegriff eingeben:",
        placeholder="Suchen Sie nach Themen, Inhalten oder Zusammenfassungen..."
    )
    
    if search_term:
        search_results = search_discussions(search_term)
        
        if search_results:
            st.success(f"**{len(search_results)} Ergebnisse für '{search_term}' gefunden:**")
            
            for i, result in enumerate(search_results[:10]):  # Top 10 Ergebnisse
                with st.expander(f"🔍 {result['topic'][:50]}..."):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**📅 Datum:** {result['timestamp'][:19].replace('T', ' ')}")
                        st.write(f"**🤖 Modelle:** {', '.join(result['models'])}")
                        st.write(f"**🔢 DB-ID:** {result['id']}")
                    
                    with col2:
                        # Relevanz-Score (falls implementiert)
                        st.metric("🎯 Relevanz", "Hoch")
                    
                    # Buttons für Suchresultate
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.button(f"📖 Anzeigen", key=f"search_load_{i}", use_container_width=True):
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
            st.warning(f"Keine Ergebnisse für '{search_term}' gefunden.")
    else:
        st.info("💡 Geben Sie einen Suchbegriff ein, um Diskussionen zu finden.")


def show_statistics_section():
    """Zeigt den Statistik-Bereich"""
    st.header("📊 Diskussions-Statistiken")
    
    stats = get_discussion_statistics()
    
    # Hauptmetriken
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💬 Gesamt-Diskussionen",
            value=stats.get('total_discussions', 0)
        )
    
    with col2:
        st.metric(
            label="📝 Gesamt-Nachrichten",
            value=stats.get('total_messages', 0)
        )
    
    with col3:
        avg_messages = 0
        if stats.get('total_discussions', 0) > 0:
            avg_messages = round(stats.get('total_messages', 0) / stats.get('total_discussions', 1), 1)
        st.metric(
            label="📊 Ø Nachrichten/Diskussion",
            value=avg_messages
        )
    
    # Letzte Diskussion
    if stats.get('latest_discussion'):
        st.subheader("🕒 Letzte Diskussion")
        latest = stats['latest_discussion']
        st.info(f"**{latest['topic']}** - {latest['timestamp'][:19].replace('T', ' ')}")
    
    # Zusätzliche Statistiken
    st.subheader("📈 Weitere Statistiken")
    
    # Hier könnten weitere Statistiken hinzugefügt werden
    st.info("💡 Erweiterte Statistiken werden in zukünftigen Versionen hinzugefügt.")


def show_backup_section():
    """Zeigt den Backup-Bereich"""
    st.header("💾 Datenbank-Backup")
    
    st.markdown("""
    Erstellen Sie ein Backup Ihrer Diskussionen, um sie zu sichern oder auf einen anderen Server zu übertragen.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Backup erstellen", use_container_width=True):
            backup_result = backup_discussions()
            if backup_result:
                st.success("✅ Backup erfolgreich erstellt!")
                st.info(f"📁 Backup-Datei: {backup_result}")
                
                # Download-Button für das Backup
                try:
                    with open(backup_result, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    
                    st.download_button(
                        label="📥 Backup herunterladen",
                        data=backup_content,
                        file_name=backup_result,
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"Fehler beim Bereitstellen des Downloads: {e}")
            else:
                st.error("❌ Backup-Erstellung fehlgeschlagen!")
    
    with col2:
        st.info("""
        **💡 Backup-Informationen:**
        - Enthält alle Diskussionen und Metadaten
        - Format: JSON
        - Kann zur Wiederherstellung verwendet werden
        - Ideal für Server-Migration
        """)


def show_discussion_details(entry):
    """Zeigt detaillierte Informationen über eine Diskussion"""
    st.subheader("ℹ️ Diskussions-Details")
    
    # Erweiterte Informationen in Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Übersicht", "🤖 Modelle", "📝 Inhalt"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**📅 Erstellungsdatum:** {entry['timestamp'][:19].replace('T', ' ')}")
            st.write(f"**🔢 Datenbank-ID:** {entry.get('db_id', 'Nicht verfügbar')}")
            st.write(f"**💬 Anzahl Nachrichten:** {len(entry.get('conversation', []))}")
        
        with col2:
            st.write(f"**📏 Thema-Länge:** {len(entry['topic'])} Zeichen")
            st.write(f"**📝 Zusammenfassung-Länge:** {len(entry.get('summary', ''))} Zeichen")
            st.write(f"**🤖 Anzahl Modelle:** {len(entry['models'])}")
    
    with tab2:
        # Technische Details der verwendeten Modelle
        from agent_metadata import format_technical_details
        tech_details = format_technical_details(entry['models'])
        st.markdown(tech_details)
    
    with tab3:
        # Inhaltliche Vorschau
        st.write("**📝 Zusammenfassung:**")
        st.markdown(entry.get('summary', 'Keine Zusammenfassung verfügbar'))
        
        if entry.get('conversation'):
            st.write("**💬 Erste Nachricht:**")
            first_agent, first_message = entry['conversation'][0]
            st.markdown(f"**{first_agent}:** {first_message[:200]}...")


def create_markdown_download(entry):
    """Erstellt einen Markdown-Download für eine Diskussion"""
    markdown_content = f"""# {entry['topic']}

**Datum:** {entry['timestamp'][:19].replace('T', ' ')}
**Modelle:** {', '.join(entry['models'])}
**DB-ID:** {entry.get('db_id', 'N/A')}

## Diskussionsverlauf

"""
    for i, (agent, message) in enumerate(entry.get('conversation', [])):
        markdown_content += f"### Turn {i+1} - {agent}\n\n{message}\n\n"
    
    markdown_content += f"## Zusammenfassung\n\n{entry.get('summary', 'Keine Zusammenfassung verfügbar')}"
    
    st.download_button(
        label="📄 Als Markdown herunterladen",
        data=markdown_content,
        file_name=f"diskussion_{entry['topic'][:30]}.md",
        mime="text/markdown",
        key=f"download_{entry.get('db_id', 'unknown')}"
    )


if __name__ == "__main__":
    main()
