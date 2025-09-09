# database_manager.py - SQLite Database Manager für Diskussions-Speicherung
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st


class DiscussionDatabase:
    """SQLite Database Manager für AI-Diskussionen"""
    
    def __init__(self, db_path: str = "discussions.db"):
        """
        Initialisiert die Datenbank
        
        Args:
            db_path: Pfad zur SQLite-Datenbank
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Erstellt die Datenbank-Tabellen falls sie nicht existieren"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Haupttabelle für Diskussionen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discussions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    models TEXT NOT NULL,  -- JSON array
                    summary TEXT NOT NULL,
                    total_turns INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabelle für einzelne Nachrichten/Turns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discussion_id INTEGER NOT NULL,
                    turn_number INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    message_content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discussion_id) REFERENCES discussions (id) ON DELETE CASCADE
                )
            ''')
            
            # Index für bessere Performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_discussion_timestamp 
                ON discussions(timestamp DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_discussion 
                ON messages(discussion_id, turn_number)
            ''')
            
            conn.commit()
    
    def save_discussion(self, topic: str, models: List[str], conversation: List[Tuple[str, str]], summary: str) -> int:
        """
        Speichert eine Diskussion in der Datenbank
        
        Args:
            topic: Diskussionsthema
            models: Liste der verwendeten Modelle
            conversation: Liste von (agent_name, message) Tupeln
            summary: Zusammenfassung der Diskussion
            
        Returns:
            ID der gespeicherten Diskussion
        """
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Hauptdiskussion speichern
            cursor.execute('''
                INSERT INTO discussions (timestamp, topic, models, summary, total_turns)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, topic, json.dumps(models), summary, len(conversation)))
            
            discussion_id = cursor.lastrowid
            
            # Einzelne Nachrichten speichern
            for turn_number, (agent_name, message_content) in enumerate(conversation, 1):
                cursor.execute('''
                    INSERT INTO messages (discussion_id, turn_number, agent_name, message_content)
                    VALUES (?, ?, ?, ?)
                ''', (discussion_id, turn_number, agent_name, message_content))
            
            conn.commit()
            return discussion_id
    
    def load_all_discussions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lädt alle Diskussionen (ohne Nachrichten-Details)
        
        Args:
            limit: Maximale Anzahl Diskussionen (neueste zuerst)
            
        Returns:
            Liste der Diskussionen
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, timestamp, topic, models, summary, total_turns, created_at
                FROM discussions 
                ORDER BY timestamp DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            discussions = []
            for row in rows:
                discussions.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'topic': row[2],
                    'models': json.loads(row[3]),
                    'summary': row[4],
                    'total_turns': row[5],
                    'created_at': row[6]
                })
            
            return discussions
    
    def load_discussion_with_messages(self, discussion_id: int) -> Optional[Dict[str, Any]]:
        """
        Lädt eine vollständige Diskussion mit allen Nachrichten
        
        Args:
            discussion_id: ID der Diskussion
            
        Returns:
            Vollständige Diskussion oder None wenn nicht gefunden
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Diskussion laden
            cursor.execute('''
                SELECT id, timestamp, topic, models, summary, total_turns, created_at
                FROM discussions 
                WHERE id = ?
            ''', (discussion_id,))
            
            discussion_row = cursor.fetchone()
            if not discussion_row:
                return None
            
            # Nachrichten laden
            cursor.execute('''
                SELECT turn_number, agent_name, message_content
                FROM messages 
                WHERE discussion_id = ?
                ORDER BY turn_number
            ''', (discussion_id,))
            
            message_rows = cursor.fetchall()
            
            # Conversation rekonstruieren
            conversation = [(row[1], row[2]) for row in message_rows]
            
            return {
                'id': discussion_row[0],
                'timestamp': discussion_row[1],
                'topic': discussion_row[2],
                'models': json.loads(discussion_row[3]),
                'conversation': conversation,
                'summary': discussion_row[4],
                'total_turns': discussion_row[5],
                'created_at': discussion_row[6]
            }
    
    def delete_discussion(self, discussion_id: int) -> bool:
        """
        Löscht eine Diskussion und alle zugehörigen Nachrichten
        
        Args:
            discussion_id: ID der zu löschenden Diskussion
            
        Returns:
            True wenn erfolgreich gelöscht, False sonst
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prüfen ob Diskussion existiert
            cursor.execute('SELECT id FROM discussions WHERE id = ?', (discussion_id,))
            if not cursor.fetchone():
                return False
            
            # Diskussion löschen (Nachrichten werden durch CASCADE automatisch gelöscht)
            cursor.execute('DELETE FROM discussions WHERE id = ?', (discussion_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def search_discussions(self, search_term: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Sucht Diskussionen nach Thema oder Inhalt
        
        Args:
            search_term: Suchbegriff
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste der gefundenen Diskussionen
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            search_pattern = f'%{search_term}%'
            
            query = '''
                SELECT DISTINCT d.id, d.timestamp, d.topic, d.models, d.summary, d.total_turns, d.created_at
                FROM discussions d
                LEFT JOIN messages m ON d.id = m.discussion_id
                WHERE d.topic LIKE ? OR d.summary LIKE ? OR m.message_content LIKE ?
                ORDER BY d.timestamp DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()
            
            discussions = []
            for row in rows:
                discussions.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'topic': row[2],
                    'models': json.loads(row[3]),
                    'summary': row[4],
                    'total_turns': row[5],
                    'created_at': row[6]
                })
            
            return discussions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über die gespeicherten Diskussionen zurück
        
        Returns:
            Dictionary mit Statistiken
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Grundstatistiken
            cursor.execute('SELECT COUNT(*) FROM discussions')
            total_discussions = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            # Häufigste Modelle
            cursor.execute('''
                SELECT models, COUNT(*) as count
                FROM discussions
                GROUP BY models
                ORDER BY count DESC
                LIMIT 5
            ''')
            model_usage = cursor.fetchall()
            
            # Neueste Diskussion
            cursor.execute('''
                SELECT timestamp, topic
                FROM discussions
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            latest = cursor.fetchone()
            
            return {
                'total_discussions': total_discussions,
                'total_messages': total_messages,
                'model_usage': [(json.loads(row[0]), row[1]) for row in model_usage],
                'latest_discussion': {
                    'timestamp': latest[0] if latest else None,
                    'topic': latest[1] if latest else None
                } if latest else None
            }
    
    def backup_to_json(self, backup_path: str) -> bool:
        """
        Erstellt ein JSON-Backup aller Diskussionen
        
        Args:
            backup_path: Pfad für die Backup-Datei
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            discussions = []
            all_discussions = self.load_all_discussions()
            
            for disc in all_discussions:
                full_disc = self.load_discussion_with_messages(disc['id'])
                if full_disc:
                    discussions.append(full_disc)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(discussions, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Backup-Fehler: {e}")
            return False


# Globale Datenbankinstanz
@st.cache_resource
def get_database() -> DiscussionDatabase:
    """Erstellt oder gibt die globale Datenbankinstanz zurück"""
    return DiscussionDatabase()


def sync_session_to_database():
    """Synchronisiert Session State mit der Datenbank"""
    if 'discussion_history' in st.session_state:
        db = get_database()
        session_discussions = st.session_state.discussion_history
        
        # Speichere neue Diskussionen die noch nicht in der DB sind
        for discussion in session_discussions:
            if 'db_id' not in discussion:  # Noch nicht in DB gespeichert
                db_id = db.save_discussion(
                    discussion['topic'],
                    discussion['models'],
                    discussion['conversation'],
                    discussion['summary']
                )
                discussion['db_id'] = db_id


def load_database_to_session(limit: Optional[int] = 10):
    """Lädt Diskussionen aus der Datenbank in den Session State"""
    db = get_database()
    db_discussions = db.load_all_discussions(limit)
    
    # Konvertiere zu Session State Format
    session_discussions = []
    for disc in db_discussions:
        full_disc = db.load_discussion_with_messages(disc['id'])
        if full_disc:
            session_discussions.append({
                'db_id': full_disc['id'],
                'timestamp': full_disc['timestamp'],
                'topic': full_disc['topic'],
                'models': full_disc['models'],
                'conversation': full_disc['conversation'],
                'summary': full_disc['summary']
            })
    
    st.session_state.discussion_history = session_discussions
