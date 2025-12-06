"""
Memory management for RaithaMithra
"""

import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass

from loguru import logger
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


@dataclass
class MemoryItem:
    """Individual memory item"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    memory_type: str = "conversation"  # conversation, knowledge, experience
    language: str = "en"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.tags is None:
            self.tags = []
        if self.embedding is None:
            self.embedding = []


class ShortTermMemory:
    """SQLite-based short-term memory for conversation history"""
    
    def __init__(self, db_path: str = "data/raithamithra.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    language TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    last_active DATETIME NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    language TEXT NOT NULL,
                    voice_enabled BOOLEAN DEFAULT 1,
                    preferred_voice TEXT,
                    location TEXT,
                    timezone TEXT,
                    updated_at DATETIME NOT NULL
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_conversation(self, session_id: str, user_id: str, user_message: str, 
                        assistant_response: str, language: str = "en", 
                        metadata: Dict[str, Any] = None) -> str:
        """Add a conversation to memory"""
        conversation_id = str(uuid.uuid4())
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO conversations 
                (id, session_id, user_id, user_message, assistant_response, language, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id, session_id, user_id, user_message, 
                assistant_response, language, datetime.utcnow().isoformat(),
                json.dumps(metadata or {})
            ))
            conn.commit()
        
        return conversation_id
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'user_id': row['user_id'],
                    'user_message': row['user_message'],
                    'assistant_response': row['assistant_response'],
                    'language': row['language'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                })
            
            return conversations[::-1]  # Reverse to get chronological order
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'user_id': row['user_id'],
                    'language': row['language'],
                    'voice_enabled': bool(row['voice_enabled']),
                    'preferred_voice': row['preferred_voice'],
                    'location': row['location'],
                    'timezone': row['timezone'],
                    'updated_at': row['updated_at']
                }
            return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, language, voice_enabled, preferred_voice, location, timezone, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    preferences.get('language', 'kn'),
                    preferences.get('voice_enabled', True),
                    preferences.get('preferred_voice'),
                    preferences.get('location'),
                    preferences.get('timezone'),
                    datetime.utcnow().isoformat()
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
        
class MemoryManager:
    """Main memory manager combining short-term and long-term memory"""
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize short-term memory
        self.short_term = ShortTermMemory()
        
        logger.info("Memory manager initialized successfully")
    
    def add_conversation(self, session_id: str, user_id: str, user_message: str, 
                        assistant_response: str, language: str = "kn", 
                        metadata: Dict[str, Any] = None) -> str:
        """Add a conversation to memory"""
        # Add to short-term memory
        conversation_id = self.short_term.add_conversation(
            session_id, user_id, user_message, assistant_response, language, metadata
        )
        
        return conversation_id
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.short_term.get_conversation_history(session_id, limit)
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        return self.short_term.get_user_preferences(user_id)
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        return self.short_term.update_user_preferences(user_id, preferences)

# Global memory manager instance
memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Get memory manager instance"""
    return memory_manager

