import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import sys
import logging
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =====================================================================
#                          SYSTEM LOGGING SETUP
# =====================================================================
logging.basicConfig(level=logging.INFO, format="[JarvisCore] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Jarvis")

class JarvisAutomationAssistant:
    def __init__(self):
        """ইঞ্জিন এবং ড্রাইভার ভ্যারিয়েবল ইনিশিয়েট করা (Lazy Loading Architecture)"""
        self.driver = None
        self.is_scrolling = False
        
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 175) 
            logger.info("Speech Engine successfully mapped.")
        except Exception as e:
            logger.critical(f"TTS initialization failed: {e}")
            sys.exit("Audio Framework Link Error.")

    def speak(self, audio_text: str):
        clean_text = audio_text.strip()
        if not clean_text:
            return
        print(f"Jarvis: {clean_text}")
        try:
            self.engine.say(clean_text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Speech Runtime Exception: {e}")

    def greet_user(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            self.speak("Good Morning!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("I am Jarvis. System protocols and automation hooks are online. How can I assist you?")

    def _init_selenium_driver(self):
        """যখন প্রয়োজন হবে তখনই ড্রাইভার রান করবে (রিসোর্স অপ্টিমাইজেশন)"""
        if self.driver is None:
            try:
                logger.info("Initializing Safe Selenium Chrome Instance...")
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                
                # ক্রোম ড্রাইভার অটো-ম্যানেজড উপায়ে লোড করা
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
                # ডিফল্ট ল্যান্ডিং পেজ ওপেন করা
                self.driver.get("https://en.wikipedia.org/wiki/Python_(programming_language)")
            except Exception as e:
                logger.error(f"Failed to trigger Webdriver: {e}")
                self.speak("Sir, web driver automation module failed to load.")

    def take_command(self) -> str:
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.pause_threshold = 1.0
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                print("\nListening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except Exception as mic_err:
            logger.error(f"Microphone hardware interface error: {mic_err}")
            return "none"

        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower().strip()
        except Exception:
            return "none"

    def _execute_scroll_loop(self, scroll_duration):
        """নন-ব্লকিং স্ক্রোলিং অপারেশন (আলাদা ব্যাকগ্রাউন্ড থ্রেডে চলবে)"""
        start_time = time.time()
        logger.info("Background smooth scroll loop active.")
        
        while time.time() - start_time < scroll_duration and self.is_scrolling:
            if self.driver:
                try:
                    self.driver.execute_script("window.scrollBy(0, 15);")
                except Exception:
                    break
            time.sleep(0.04)
            
        self.is_scrolling = False
        logger.info("Background scroll finished safely.")

    def trigger_smooth_scroll(self, duration=8):
        """ব্লকিং এড়াতে স্ক্রোল টাস্ককে মেইন থ্রেড থেকে ডিটাচ করা"""
        self._init_selenium_driver()
        if not self.driver:
            return
            
        if not self.is_scrolling:
            self.is_scrolling = True
            # মাল্টি-থ্রেডিং এর মাধ্যমে স্ক্রোলিং চালু করা যাতে Jarvis কথা শুনতে পারে একই সাথে
            scroll_thread = threading.Thread(target=self._execute_scroll_loop, args=(duration,))
            scroll_thread.daemon = True
            scroll_thread.start()
        else:
            logger.warning("Scroll request denied. Process already active.")

    def shutdown_driver(self):
        """মেমোরি লিক ও জম্বি প্রসেস ডিফেন্স"""
        self.is_scrolling = False
        if self.driver:
            logger.info("Terminating Selenium instances...")
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def run_main_pipeline(self):
        self.greet_user()
        
        while True:
            query = self.take_command()
            
            if query == "none":
                continue

            if 'wikipedia' in query:
                self.speak('Searching target index on Wikipedia...')
                search_query = query.replace("wikipedia", "").strip()
                if not search_query:
                    self.speak("What should I search, Sir?")
                    continue
                try:
                    results = wikipedia.summary(search_query, sentences=2, auto_suggest=False)
                    self.speak("According to structural details:")
                    self.speak(results)
                except wikipedia.exceptions.DisambiguationError:
                    self.speak("The query matches multiple pages. Please be more specific.")
                except Exception:
                    self.speak("I couldn't find any relevant details on Wikipedia matching the query.")

            elif 'open google' in query:
                self.speak("Opening Google Interface.")
                webbrowser.open("https://www.google.com")

            elif 'open youtube' in query:
                self.speak("Opening YouTube Interface.")
                webbrowser.open("https://www.youtube.com")

            elif 'the time' in query:
                str_time = datetime.datetime.now().strftime("%I:%M %p")    
                self.speak(f"Sir, the system clock marks {str_time}")

            elif 'scroll down' in query:
                self.speak("Scrolling browser downlink, sir.")
                self.trigger_smooth_scroll(duration=8)

            elif any(token in query for token in ['offline', 'stop', 'quit', 'exit']):
                self.speak("Deactivating automated nodes. Moving Jarvis offline. Goodbye, Sir!")
                self.shutdown_driver()
                break

# =====================================================================
# ENTRY BLOCK AND CLEAN SHUTDOWN HANDLER
# =====================================================================
if __name__ == "__main__":
    jarvis_bot = JarvisAutomationAssistant()
    try:
        jarvis_bot.run_main_pipeline()
    except KeyboardInterrupt:
        logger.info("Emergency terminal interrupt caught.")
        jarvis_bot.shutdown_driver()
        sys.exit(0)
