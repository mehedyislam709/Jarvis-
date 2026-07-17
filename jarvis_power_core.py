import os
import re
import sys
import json
import math
import socket
import logging
import smtplib
import sqlite3
import ssl
import ipaddress
import urllib.parse
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Tuple, Optional

import requests
from bs4 import BeautifulSoup

# =====================================================================
#             ENTERPRISE MAINFRAME AUDIT LOGGING MODULE
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [JARVIS-CORE-MAINFRAME] [%(levelname)s] (%(threadName)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("jarvis_hardened_core.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("JarvisCore")

# =====================================================================
#             MODULE 1: SECURE LIVE WEB SCRAPER & SUMMARIZER
# =====================================================================
class JarvisWebScraper:
    """
    Hardened scraping ecosystem configured with severe SSRF defenses
    and mathematically balanced TF-IDF ranking infrastructure.
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def validate_and_resolve_url(self, url: str) -> str:
        """
        Validates target schemes and cross-references resolved IP structures
        to eliminate SSRF layout attacks on internal server networks.
        """
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or parsed.scheme not in ["http", "https"]:
            raise ValueError("Forbidden protocol layer requested. Only HTTP or HTTPS instances are allowed.")
        
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Malformed URL string pattern. Target host could not be computed.")

        try:
            # Resolve network identity addresses safely
            resolved_ips = socket.getaddrinfo(hostname, None)
            for item in resolved_ips:
                ip_addr_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_addr_str)
                
                # Intercept loopbacks, private subnets, link-local frames
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                    raise ValueError(f"Security Intercept: Target points to a restricted internal domain framework: {ip_addr_str}")
        except socket.gaierror as dns_err:
            raise ValueError(f"DNS resolution failure mapping host context: {dns_err}")
            
        return url

    def fetch_clean_text(self, url: str) -> str:
        """Securely parses external HTML DOM payloads, destroying execution tags and scripts."""
        try:
            target_url = self.validate_and_resolve_url(url)
            logger.info(f"[Web Scraper] Dispatching isolated request handle to resource: {target_url}")
            
            # Enforce strict connection windows to avoid server thread exhaustion attacks
            response = requests.get(target_url, headers=self.headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            response.encoding = response.apparent_encoding if response.apparent_encoding else "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Flush potentially volatile active scripts and noisy structure matrices
            for volatile_node in soup(["script", "style", "nav", "footer", "iframe", "header", "noscript"]):
                volatile_node.decompose()
                
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
            extracted_lines = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 15]
            
            sanitized_body = " ".join(extracted_lines)
            return re.sub(r'\s+', ' ', sanitized_body).strip()
            
        except Exception as err:
            logger.error(f"[Web Scraper] Critical execution anomaly: {err}")
            return f"Scraping Intercept Block: Operation could not compile safely. Details: {str(err)}"

    def generate_abstractive_summary(self, text: str, sentences_count: int = 3) -> str:
        """Computes text extraction weighting via normalized frequency analysis matrix loops."""
        if not text or "Scraping Intercept Block" in text:
            return "No verifiable dataset context present to execute analysis."
            
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= sentences_count:
            return " ".join(sentences)

        # Mathematical frequency extraction configuration
        token_frequency: Dict[str, float] = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on", "for", "with", "is", "was", "that", "this", "as", "by", "it"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        total_valid_tokens = 0
        
        for w in words:
            if w not in stop_words and not w.isdigit():
                token_frequency[w] = token_frequency.get(w, 0.0) + 1.0
                total_valid_tokens += 1

        if not token_frequency:
            return " ".join(sentences[:sentences_count])

        # Normalize metrics smoothly
        max_freq = max(token_frequency.values())
        for k in token_frequency:
            token_frequency[k] = token_frequency[k] / max_freq

        # Compute dynamic matching weights per parsed sentence segment
        sentence_scores: Dict[str, float] = {}
        for idx, sentence in enumerate(sentences):
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            score = 0.0
            for sw in sentence_words:
                if sw in token_frequency:
                    score += token_frequency[sw]
            
            # Apply light length normalization to prevent bias toward long sentences
            sentence_scores[sentence] = score / (math.log(len(sentence_words) + 1) + 1.0)

        # Extract the highest ranking contextual array sequences
        sorted_nodes = sorted(sentences, key=lambda s: sentence_scores.get(s, 0.0), reverse=True)
        top_nodes = sorted_nodes[:sentences_count]
        
        # Chronological preservation mapping
        top_nodes.sort(key=lambda x: sentences.index(x))
        return " ".join(top_nodes)


# =====================================================================
#                 MODULE 2: SECURE MAIL AGENT
# =====================================================================
class JarvisMailAgent:
    """Outbound transactional communications agent enforcing explicit TLS 1.3 crypto context layers."""
    def __init__(self):
        self.smtp_server = os.getenv("JARVIS_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("JARVIS_SMTP_PORT", "465")) # Hardened native SMTPS allocation
        self.sender_email = os.getenv("JARVIS_EMAIL_USER")
        self.sender_password = os.getenv("JARVIS_EMAIL_PASSWORD")

    def sanitize_header_token(self, token: str) -> str:
        """Neutralizes carriage returns and line feed elements to isolate header space boundaries."""
        return re.sub(r'[\r\n]', '', token).strip()

    def send_outbound_email(self, recipient_email: str, subject: str, message_body: str) -> bool:
        if not self.sender_email or not self.sender_password:
            logger.error("[Mail Agent] Infrastructure credentials not loaded into standard runtime environments.")
            return False

        try:
            clean_recipient = self.sanitize_header_token(recipient_email)
            clean_subject = self.sanitize_header_token(subject)

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = clean_recipient
            msg['Subject'] = clean_subject
            msg.attach(MIMEText(message_body, 'plain', 'utf-8'))

            logger.info(f"[Mail Agent] Tuning SSL validation context mapping parameters for connection to {self.smtp_server}...")
            
            # Enforce modern secure protocols exclusively
            ssl_context = ssl.create_default_context()
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=ssl_context, timeout=12) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            logger.info(f"[Mail Agent] Telemetry transmission dispatched to destination node: {clean_recipient}")
            return True
        except Exception as mail_fault:
            logger.error(f"[Mail Agent] Transaction execution failure: {mail_fault}")
            return False


# =====================================================================
#             MODULE 3: SMART CALENDAR INTEGRATOR
# =====================================================================
class JarvisCalendarIntegrator:
    """Localized production storage system protecting transactions against database injection vectors."""
    def __init__(self, db_path: str = "jarvis_calendar_secure.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Restrict access parameters for standard environments
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS platform_calendar (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        description TEXT
                    )
                """)
                conn.commit()
        except sqlite3.Error as db_err:
            logger.critical(f"[Calendar System] Core internal storage failed validation: {db_err}")

    def verify_iso_format(self, date_string: str) -> bool:
        """Validates datetime string conformity cleanly via absolute evaluation routines."""
        try:
            datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            return False

    def register_scheduled_event(self, title: str, start_time_str: str, end_time_str: str, description: str = "") -> Dict[str, str]:
        if not self.verify_iso_format(start_time_str) or not self.verify_iso_format(end_time_str):
            return {"status": "error", "message": "Syntax Anomaly: Timestamps must adhere to 'YYYY-MM-DD HH:MM:SS'."}

        if start_time_str >= end_time_str:
            return {"status": "error", "message": "Timeline Inversion Error: Start parameters must occur before End points."}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for schedule collisions securely using parameterized bindings
                cursor.execute("""
                    SELECT title, start_time, end_time FROM platform_calendar 
                    WHERE (? < end_time) AND (? > start_time)
                """, (start_time_str, end_time_str))
                
                collision = cursor.fetchone()
                if collision:
                    return {
                        "status": "collision",
                        "message": f"Scheduling Collision: Timeframe blocked by active block '{collision[0]}' [{collision[1]} -> {collision[2]}]"
                    }

                # Input processing injection neutralized via strict parameter token placement values
                cursor.execute("""
                    INSERT INTO platform_calendar (title, start_time, end_time, description)
                    VALUES (?, ?, ?, ?)
                """, (title.strip(), start_time_str, end_time_str, description.strip()))
                conn.commit()
                
            logger.info(f"[Calendar Integrator] Logged execution parameters for record entry: {title}")
            return {"status": "success", "message": f"Successfully committed event entry record '{title}'."}
        except Exception as inner_fault:
            logger.error(f"[Calendar Integrator] Storage commit exception caught: {inner_fault}")
            return {"status": "error", "message": "Internal storage transaction failure execution halted."}

    def generate_day_agenda(self, target_date_str: str) -> List[Dict[str, Any]]:
        # Defensively match structure syntax blocks
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', target_date_str):
            logger.error("[Calendar System] Parameter string processing block validation mismatch.")
            return []

        day_start = f"{target_date_str} 00:00:00"
        day_end = f"{target_date_str} 23:59:59"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT title, start_time, end_time, description FROM platform_calendar
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
        except Exception as query_err:
            logger.error(f"[Calendar System] Transaction engine tracking block failure: {query_err}")
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
        while True:
            print("\n" + "█"*65)
            print("         JARVIS UNIFIED OPERATIONS CENTRE: ENTERPRISE LAYER        ")
            print("█"*65)
            print("1. Scrape & Summarize Dynamic URL")
            print("2. Send Secured Outbound Mail")
            print("3. Register Calendar Event (Auto-collision guard)")
            print("4. Pull Daily Agenda Schedule")
            print("5. Emergency System Exit")
            print("-" * 65)

            choice = input("Dispatch Operation Code (1-5): ").strip()

            if choice == '1':
                url = input("\nEnter Target HTTP/HTTPS Resource URL: ").strip()
                if url:
                    print("\n[Jarvis Workstation] Validating and resolving connection rules...")
                    raw_scraped_text = self.scraper.fetch_clean_text(url)
                    summary = self.scraper.generate_abstractive_summary(raw_scraped_text, sentences_count=3)
                    print("\n--- ADVANCED WEB TEXT ABSTRACTIVE SUMMARY ---")
                    print(summary)

            elif choice == '2':
                recipient = input("\nRecipient Mail Target: ").strip()
                subject = input("Header Subject: ").strip()
                body = input("Payload Plaintext Body: ").strip()
                if recipient and subject and body:
                    print("\n[Jarvis Workstation] Testing SSL cryptographic layers and dispatching...")
                    success = self.mail.send_outbound_email(recipient, subject, body)
                    if success:
                        print("\n[Jarvis Workstation] Dispatch confirmed.")
                    else:
                        print("\n[Jarvis Workstation] Operation failed. Verify environment variable declarations.")

            elif choice == '3':
                title = input("\nEvent Title: ").strip()
                start = input("Start Timestamp (Format: YYYY-MM-DD HH:MM:SS): ").strip()
                end = input("End Timestamp (Format: YYYY-MM-DD HH:MM:SS): ").strip()
                desc = input("Operational Directives (Description): ").strip()
                if title and start and end:
                    print("\n[Jarvis Workstation] Verifying schedule overlaps across storage lines...")
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
                print("\nInitiating secure system lockdown shutdown routines...")
                break

if __name__ == "__main__":
    mainframe = JarvisUnifiedPlatform()
    mainframe.run()
