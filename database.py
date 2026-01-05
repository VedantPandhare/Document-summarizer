import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

class SummaryDatabase:
    def __init__(self, db_path: str = "summaries.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the database and tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create summaries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    original_text TEXT,
                    summary TEXT NOT NULL,
                    summary_style TEXT NOT NULL,
                    quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    processing_time REAL,
                    word_count INTEGER,
                    summary_word_count INTEGER
                )
            ''')
            
            # Create users table for future user management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create summary_analytics table for tracking usage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summary_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_id INTEGER,
                    user_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (summary_id) REFERENCES summaries (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON summaries(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON summaries(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_type ON summaries(document_type)')
            
            conn.commit()
    
    def save_summary(self, user_id: str, document_name: str, document_type: str, 
                    original_text: str, summary: str, summary_style: str, 
                    quality_score: Optional[float] = None, file_size: Optional[int] = None,
                    processing_time: Optional[float] = None, word_count: Optional[int] = None,
                    summary_word_count: Optional[int] = None) -> int:
        """Save a new summary to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO summaries (
                    user_id, document_name, document_type, original_text, summary, 
                    summary_style, quality_score, file_size, processing_time, 
                    word_count, summary_word_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, document_name, document_type, original_text, summary, 
                summary_style, quality_score, file_size, processing_time, 
                word_count, summary_word_count
            ))
            
            summary_id = cursor.lastrowid
            conn.commit()
            return summary_id
    
    def get_user_summaries(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get summaries for a specific user with pagination."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM summaries 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_summary_by_id(self, summary_id: int) -> Optional[Dict]:
        """Get a specific summary by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM summaries WHERE id = ?', (summary_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def search_summaries(self, user_id: str, query: str, limit: int = 20) -> List[Dict]:
        """Search summaries by document name or content."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            search_query = f"%{query}%"
            cursor.execute('''
                SELECT * FROM summaries 
                WHERE user_id = ? AND (
                    document_name LIKE ? OR 
                    summary LIKE ? OR 
                    original_text LIKE ?
                )
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, search_query, search_query, search_query, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_summary(self, summary_id: int, user_id: str) -> bool:
        """Delete a summary (only if it belongs to the user)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM summaries 
                WHERE id = ? AND user_id = ?
            ''', (summary_id, user_id))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count > 0
    
    def update_summary(self, summary_id: int, user_id: str, 
                      summary: str, quality_score: Optional[float] = None) -> bool:
        """Update an existing summary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if quality_score is not None:
                cursor.execute('''
                    UPDATE summaries 
                    SET summary = ?, quality_score = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (summary, quality_score, summary_id, user_id))
            else:
                cursor.execute('''
                    UPDATE summaries 
                    SET summary = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (summary, summary_id, user_id))
            
            updated_count = cursor.rowcount
            conn.commit()
            return updated_count > 0
    
    def get_summary_statistics(self, user_id: str) -> Dict:
        """Get summary statistics for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total summaries
            cursor.execute('SELECT COUNT(*) FROM summaries WHERE user_id = ?', (user_id,))
            total_summaries = cursor.fetchone()[0]
            
            # Total documents processed
            cursor.execute('SELECT COUNT(DISTINCT document_name) FROM summaries WHERE user_id = ?', (user_id,))
            total_documents = cursor.fetchone()[0]
            
            # Average quality score
            cursor.execute('SELECT AVG(quality_score) FROM summaries WHERE user_id = ? AND quality_score IS NOT NULL', (user_id,))
            avg_quality = cursor.fetchone()[0] or 0
            
            # Most used summary style
            cursor.execute('''
                SELECT summary_style, COUNT(*) as count 
                FROM summaries 
                WHERE user_id = ? 
                GROUP BY summary_style 
                ORDER BY count DESC 
                LIMIT 1
            ''', (user_id,))
            favorite_style = cursor.fetchone()
            favorite_style = favorite_style[0] if favorite_style else "None"
            
            # Total words processed
            cursor.execute('SELECT SUM(word_count) FROM summaries WHERE user_id = ?', (user_id,))
            total_words = cursor.fetchone()[0] or 0
            
            return {
                "total_summaries": total_summaries,
                "total_documents": total_documents,
                "average_quality": round(avg_quality, 2),
                "favorite_style": favorite_style,
                "total_words_processed": total_words
            }
    
    def get_recent_summaries(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get summaries from the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM summaries 
                WHERE user_id = ? AND created_at >= datetime('now', '-{} days')
                ORDER BY created_at DESC
            '''.format(days), (user_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def cleanup_old_summaries(self, user_id: str, days: int = 30) -> int:
        """Remove summaries older than N days for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM summaries 
                WHERE user_id = ? AND created_at < datetime('now', '-{} days')
            '''.format(days), (user_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

# Global database instance
db = SummaryDatabase()


