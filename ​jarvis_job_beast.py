import sqlite3
import datetime
import logging
import re
from typing import List, Dict, Set
from contextlib import contextmanager

# Professional Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] (CAREER-FORTRESS) %(message)s')

class DatabaseManager:
    """Provides thread-safe access to the SQLite database."""
    def __init__(self, db_file="jarvis_career_fortress.db"):
        self.db_file = db_file
        self._initialize_schema()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT NOT NULL, 
                    company TEXT NOT NULL, 
                    platform TEXT, 
                    status TEXT DEFAULT 'TRACKING', 
                    reminder_date TEXT, 
                    jd_text TEXT
                )
            """)
            conn.commit()

class CVAnalyzer:
    """The 'Brain': Advanced NLP-driven resume tailoring."""
    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        # Improved Regex: Captures alphanumeric keywords and removes noise
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stopwords = {'with', 'that', 'this', 'from', 'also', 'will', 'have'}
        return {word for word in words if word not in stopwords}

    @classmethod
    def get_tailoring_score(cls, resume_text: str, jd_text: str) -> Dict[str, Any]:
        resume_keywords = cls.extract_keywords(resume_text)
        jd_keywords = cls.extract_keywords(jd_text)
        
        matches = jd_keywords.intersection(resume_keywords)
        missing = jd_keywords.difference(resume_keywords)
        
        score = (len(matches) / len(jd_keywords) * 100) if jd_keywords else 0
        return {"score": round(score, 2), "missing": list(missing)}

class JarvisJobManager(DatabaseManager):
    """Orchestrator for Job Asset Management."""
    
    def add_job(self, title: str, company: str, platform: str, reminder_date: str, jd_text: str):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (title, company, platform, reminder_date, jd_text) 
                VALUES (?, ?, ?, ?, ?)""", (title, company, platform, reminder_date, jd_text))
            conn.commit()
            logging.info(f"Job locked: {title} at {company}")

    def get_due_reminders(self) -> List[tuple]:
        today = datetime.date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT title, company FROM jobs WHERE reminder_date = ?", (today,))
            return cursor.fetchall()

    def display_dashboard(self):
        with self.get_connection() as conn:
            jobs = conn.execute("SELECT * FROM jobs").fetchall()
            print(f"\n{'='*10} JARVIS CAREER DASHBOARD {'='*10}")
            for job in jobs:
                print(f"[{job[0]}] {job[1]} @ {job[2]} | Status: {job[4]}")
