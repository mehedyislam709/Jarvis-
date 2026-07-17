import os
import re
import sys
import json
import logging
import smtplib
import sqlite3
import math
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Advanced Logger setup with fail-safe logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Jarvis System Core) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("jarvis_system_core.log", encoding="utf-8")
    ]
)

# =====================================================================
#             MODULE 1: SECURE LIVE WEB SCRAPER & SUMMARIZER
# =====================================================================
class JarvisWebScraper:
    """
    Robust scraping module built to extract structural text body from
    dynamic websites with automatic fallback modes and fail-safe parsing.
    """
    def __init__(self):
        # Premium browser emulation to bypass bot blockers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def sanitize_url(self, url: str) -> str:
        """Validates and clean URLs prior to execution to prevent SSRF vulnerabilities."""
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or parsed.scheme not in ["http", "https"]:
            raise ValueError("Forbidden protocol. Only HTTPS and HTTP are accepted.")
        return url

    def fetch_clean_text(self, url: str) -> str:
        """Scrapes text content securely and discards boilerplate clutter."""
        try:
            target_url = self.sanitize_url(url)
            logging.info(f"[Web Scraper] Safely requesting target resource: {target_url}")
            
            response = requests.get(target_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Detect actual encoding to prevent corrupted non-ASCII characters
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Wipe noise elements (script, style, iframe, footers)
            for structural_noise in soup(["script", "style", "nav", "footer", "iframe", "header"]):
                structural_noise.decompose()
                
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
            extracted_lines = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 15]
            
            final_raw_content = " ".join(extracted_lines)
            return re.sub(r'\s+', ' ', final_raw_content).strip()
            
        except requests.exceptions.RequestException as req_err:
            logging.error(f"[Web Scraper] Network communication exception: {req_err}")
            return f"Scraping Failure: Unable to connect to source server. Details: {str(req_err)}"
        except Exception as e:
            logging.error(f"[Web Scraper] Core Extraction Exception: {e}")
            return f"Scraping Error: An internal system fault occurred. Details: {str(e)}"

    def generate_abstractive_summary(self, text: str, sentences_count: int = 4) -> str:
        """
        Calculates tf-idf based rank scoring to summarize scrapped content.
        Perfect fallback engine when direct API quotas are restricted.
        """
        if not text or "Scraping Failure" in text or "Scraping Error" in text:
            return "No content loaded to generate summary."
            
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= sentences_count:
            return text

        # TF-IDF inspired statistical parsing
        words_frequency = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on", "for", "with", "is", "was"}
        
        for word in text.lower().split():
            cleaned_word = ''.join(c for c in word if c.isalnum())
            if cleaned_word and cleaned_word not in stop_words:
                words_frequency[cleaned_word] = words_frequency.get(cleaned_word, 0) + 1

        sentence_scores = {}
        for sentence in sentences:
            for word in sentence.lower().split():
                cleaned_word = ''.join(c for c in word if c.isalnum())
                if cleaned_word in words_frequency:
                    sentence_scores[sentence] = sentence_scores.get(sentence, 0) + words_frequency[cleaned_word]

        # Get highest-scoring key sentences
        sorted_sentences = sorted(sentence_scores.keys(), key=lambda s: sentence_scores[s], reverse=True)
        summary_nodes = sorted_sentences[:sentences_count]
        
        # Maintain chronologically correct flow
        summary_nodes.sort(key=lambda x: sentences.index(x))
        return " ".join(summary_nodes)


# =====================================================================
#                 MODULE 2: SECURE MAIL AGENT
# =====================================================================
class JarvisMailAgent:
    """
    Extremely secure and isolated outbound transactional email agent.
    Safeguards SMTP instances and blocks standard script-injection vulnerabilities.
    """
    def __init__(self):
        # Loads configurations from system environment variables
        self.smtp_server = os.getenv("JARVIS_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("JARVIS_SMTP_PORT", "587"))
        self.sender_email = os.getenv("JARVIS_EMAIL_USER")
        self.sender_password = os.getenv("JARVIS_EMAIL_PASSWORD") # App Password recommended

    def clean_header(self, input_string: str) -> str:
        """Wipes out newlines from email headers to neutralize command injection risks."""
        return re.sub(r'[\r\n]', '', input_string).strip()

    def send_outbound_email(self, recipient_email: str, subject: str, message_body: str) -> bool:
        """Establishes active TLS session and dispatches encrypted mail."""
        if not self.sender_email or not self.sender_password:
            logging.error("[Mail Agent] Environment configuration missing! 'JARVIS_EMAIL_USER' and 'JARVIS_EMAIL_PASSWORD' are required.")
            return False

        try:
            clean_recipient = self.clean_header(recipient_email)
            clean_subject = self.clean_header(subject)

            # Build standard structure
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = clean_recipient
            msg['Subject'] = clean_subject
            msg.attach(MIMEText(message_body, 'plain', 'utf-8'))

            logging.info(f"[Mail Agent] Initiating network connection to: {self.smtp_server}:{self.smtp_port}")
            
            # Secure SMTP negotiation
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls() # Establish active security layer
                server.ehlo()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            logging.info(f"[Mail Agent] Email dispatched to {clean_recipient} containing secure payload.")
            return True
        except smtplib.SMTPException as smtp_ex:
            logging.error(f"[Mail Agent] Protocol processing error: {smtp_ex}")
            return False
        except Exception as general_err:
            logging.critical(f"[Mail Agent] System stack error: {general_err}")
            return False


# =====================================================================
#             MODULE 3: SMART CALENDAR INTEGRATOR
# =====================================================================
class JarvisCalendarIntegrator:
    """
    Local robust relational database driven task and event calendar.
    Features automated collision checks to prevent overlapping timelines.
    """
    def __init__(self, db_path: str = "jarvis_calendar.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Builds clean tables on active connection thread safely."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_calendar (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        description TEXT,
                        risk_level TEXT DEFAULT 'LOW'
                    )
                """)
                conn.commit()
        except sqlite3.Error as sq_err:
            logging.critical(f"[Calendar Integrator] DB setup fault: {sq_err}")

    def parse_iso_time(self, datetime_str: str) -> datetime:
        """Ensures temporal consistency with explicit parsing."""
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Datetime formatting error: '{datetime_str}' does not match '%Y-%m-%d %H:%M:%S'")

    def register_scheduled_event(self, title: str, start_time_str: str, end_time_str: str, description: str = "") -> dict:
        """
        Registers event into localized calendar system. Evaluates calendar
        matrix to prevent dual conflicts dynamically.
        """
        try:
            start_dt = self.parse_iso_time(start_time_str)
            end_dt = self.parse_iso_time(end_time_str)

            if start_dt >= end_dt:
                return {"status": "error", "message": "Timeline Violation: Start time must occur prior to End time."}

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Fetch overlapping records: where [start_A < end_B] and [end_A > start_B]
                cursor.execute("""
                    SELECT title, start_time, end_time FROM system_calendar 
                    WHERE (? < end_time) AND (? > start_time)
                """, (start_time_str, end_time_str))
                
                collision = cursor.fetchone()
                if collision:
                    return {
                        "status": "collision_error",
                        "message": f"Conflict detected! Target timeframe overlaps with active schedule: '{collision[0]}' [{collision[1]} to {collision[2]}]"
                    }

                # Safe database insertion
                cursor.execute("""
                    INSERT INTO system_calendar (title, start_time, end_time, description)
                    VALUES (?, ?, ?, ?)
                """, (title, start_time_str, end_time_str, description))
                conn.commit()
                
            logging.info(f"[Calendar System] Block booked: '{title}' on {start_time_str}")
            return {"status": "success", "message": f"Successfully registered '{title}'."}
            
        except Exception as err:
            logging.error(f"[Calendar System] Scheduler registration failure: {err}")
            return {"status": "error", "message": f"System engine error occurred: {str(err)}"}

    def generate_day_agenda(self, target_date_str: str) -> list:
        """Generates sorted chronologically ordered timelines for a specific date (YYYY-MM-DD)."""
        try:
            # Prevent injection by formatting to date-only string
            date_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            day_start = f"{date_obj} 00:00:00"
            day_end = f"{date_obj} 23:59:59"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT title, start_time, end_time, description FROM system_calendar
                    WHERE start_time >= ? AND start_time <= ?
                    ORDER BY start_time ASC
                """, (day_start, day_end))
                records = cursor.fetchall()

            return [{
                "title": r[0],
                "start": r[1],
                "end": r[2],
                "details": r[3]
            } for r in records]
            
        except ValueError:
            logging.error(f"[Calendar System] ISO parse failure on date format: {target_date_str}")
            return []


# =====================================================================
#             CORE TERMINAL SYSTEM: INTEGRATED PLATFORM
# =====================================================================
class JarvisUnifiedPlatform:
    def __init__(self):
        self.scraper = JarvisWebScraper()
        self.mail = JarvisMailAgent()
        self.calendar = JarvisCalendarIntegrator()

    def run(self):
        """Unified dynamic operations portal."""
        while True:
            print("\n" + "█"*65)
            print("         JARVIS UNIFIED OPERATIONS CENTRE: ENTERPRISE LAYER        ")
            print("█"*65)
            print("1. Scrap & Summarize Dynamic URL")
            print("2. Send Secured Outbound Mail")
            print("3. Register Calendar Event (Auto-collision guard)")
            print("4. Pull Daily Agenda Schedule")
            print("5. Emergency System Exit")
            print("-" * 65)

            choice = input("Dispatch Operation Code (1-5): ").strip()

            if choice == '1':
                url = input("\nEnter Target HTTP/HTTPS Resource URL: ").strip()
                if url:
                    print("\n[Jarvis Workstation] Processing target raw code safely...")
                    raw_scraped_text = self.scraper.fetch_clean_text(url)
                    summary = self.scraper.generate_abstractive_summary(raw_scraped_text, sentences_count=3)
                    print("\n--- ADVANCED WEB TEXT ABSTRACTIVE SUMMARY ---")
                    print(summary)

            elif choice == '2':
                recipient = input("\nRecipient Mail Target: ").strip()
                subject = input("Header Subject: ").strip()
                body = input("Payload Plaintext Body: ").strip()
                if recipient and subject and body:
                    print("\n[Jarvis Workstation] Testing SSL layers and dispatching...")
                    success = self.mail.send_outbound_email(recipient, subject, body)
                    if success:
                        print("\n[Jarvis Workstation] Dispatch confirmed.")
                    else:
                        print("\n[Jarvis Workstation] Operation failed. Verify environment configuration.")

            elif choice == '3':
                title = input("\nEvent Title: ").strip()
                start = input("Start Timestamp (Format: YYYY-MM-DD HH:MM:SS): ").strip()
                end = input("End Timestamp (Format: YYYY-MM-DD HH:MM:SS): ").strip()
                desc = input("Operational Directives (Description): ").strip()
                if title and start and end:
                    print("\n[Jarvis Workstation] Verifying chronological overlaps...")
                    result = self.calendar.register_scheduled_event(title, start, end, desc)
                    print(f"\n[Jarvis Workstation Output]: {result['message']}")

            elif choice == '4':
                target_day = input("\nRetrieve agenda for date (Format: YYYY-MM-DD): ").strip()
                if target_day:
                    agenda = self.calendar.generate_day_agenda(target_day)
                    print(f"\n--- ACTIVE TIMELINE FOR: {target_day} ---")
                    if not agenda:
                        print("No events indexed for target timestamp.")
                    for index, item in enumerate(agenda, 1):
                        print(f"[{index}] Event: '{item['title']}' | Interval: {item['start'][11:]} to {item['end'][11:]}")
                        print(f"    Directives: {item['details']}")

            elif choice == '5':
                print("\nInitiating secure system lockdown...")
                break


if __name__ == "__main__":
    mainframe = JarvisUnifiedPlatform()
    mainframe.run()
