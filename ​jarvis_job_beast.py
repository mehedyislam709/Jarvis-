import sqlite3
import datetime
import logging
import re
from collections import Counter
from typing import List, Dict

# Setup ultra-durable logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class JobDatabase:
    """ACID-compliant storage controller for all job assets."""
    def __init__(self, db_file="jarvis_career_fortress.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY, title TEXT, company TEXT, platform TEXT, 
                status TEXT, reminder_date DATE, jd_text TEXT
            )
        """)
        self.conn.commit()

class CVAnalyzer:
    """The 'Brain': Analyzes job descriptions and tailors CV/Resume."""
    @staticmethod
    def extract_keywords(text: str) -> set:
        # Simple NLP logic: Remove common words and keep technical keywords
        words = re.findall(r'\w+', text.lower())
        stopwords = {'the', 'a', 'and', 'to', 'for', 'with', 'in', 'of', 'is'}
        return set(word for word in words if word not in stopwords and len(word) > 3)

    @classmethod
    def get_tailoring_score(cls, resume_text: str, jd_text: str) -> Dict:
        resume_keywords = cls.extract_keywords(resume_text)
        jd_keywords = cls.extract_keywords(jd_text)
        
        missing = jd_keywords - resume_keywords
        match_score = len(jd_keywords & resume_keywords) / len(jd_keywords) * 100
        
        return {"score": round(match_score, 2), "missing_keywords": list(missing)}

class JarvisJobManager(JobDatabase):
    def __init__(self):
        super().__init__()

    def search_jobs(self, query: str, platforms: List[str]):
        """Multi-platform search simulation (Integration Hook)."""
        logging.info(f"Scanning platforms: {platforms} for '{query}'...")
        # এখানে API Call হবে, বর্তমানে এটি সিমুলেটেড রেজাল্ট দেখাচ্ছে
        return [{"title": "Senior AI Engineer", "company": "Global Corp", "platform": "LinkedIn"}]

    def add_job(self, title, company, platform, reminder_date, jd_text):
        self.cursor.execute("INSERT INTO jobs (title, company, platform, status, reminder_date, jd_text) VALUES (?,?,?,?,?,?)",
                           (title, company, platform, "TRACKING", reminder_date, jd_text))
        self.conn.commit()
        logging.info(f"Job '{title}' successfully locked into the database.")

    def check_reminders(self):
        """Auto-Reminder Logic: Scans for tasks due today."""
        today = datetime.date.today().isoformat()
        self.cursor.execute("SELECT title, company FROM jobs WHERE reminder_date = ?", (today,))
        due_tasks = self.cursor.fetchall()
        for task in due_tasks:
            logging.warning(f"ACTION REQUIRED: Follow-up for {task[0]} at {task[1]} today!")

    def show_dashboard(self):
        """Renders Smart Dashboard."""
        self.cursor.execute("SELECT * FROM jobs")
        jobs = self.cursor.fetchall()
        print("\n--- JARVIS CAREER DASHBOARD ---")
        for job in jobs:
            print(f"ID: {job[0]} | Role: {job[1]} | Company: {job[2]} | Status: {job[4]}")

# --- EXECUTION ZONE ---
if __name__ == "__main__":
    jarvis = JarvisJobManager()
    
    # 1. Search Logic
    jarvis.search_jobs("Python Developer", ["LinkedIn", "Indeed"])
    
    # 2. Add Job & JD
    sample_jd = "We need an expert in Python, Machine Learning, and SQL"
    jarvis.add_job("AI Dev", "TechGiant", "LinkedIn", datetime.date.today().isoformat(), sample_jd)
    
    # 3. CV Tailoring Test
    my_resume = "I am an expert in Python and SQL"
    analysis = CVAnalyzer.get_tailoring_score(my_resume, sample_jd)
    print(f"\nCV Tailoring Match: {analysis['score']}%")
    print(f"Missing Keywords: {analysis['missing_keywords']}")
    
    # 4. Check Reminders
    jarvis.check_reminders()
    
    # 5. Dashboard
    jarvis.show_dashboard()
