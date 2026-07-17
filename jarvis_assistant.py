import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import sys
import logging
import subprocess

# এন্টারপ্রাইজ গ্রেড লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO, format="[JarvisCore] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Jarvis")

class JarvisAssistant:
    def __init__(self):
        """ভয়েস ইঞ্জিন এবং স্পীচ রিকগনিশন মডিউল প্রপারলি ইনিশিয়েট করা"""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                # voices[0] = Male, voices[1] = Female (ভয়েস অ্যারে বাউন্ড চেক)
                self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 175)  # স্পীকিং স্পীড অপ্টিমাইজড
            self.engine.setProperty('volume', 1.0)
            logger.info("Text-to-Speech engine initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize TTS engine: {e}")
            sys.exit("Critical Error: Audio system failure.")

    def speak(self, audio_text: str):
        """ইউজার ইন্টারফেসে টেক্সট প্রিন্ট এবং ভয়েস জেনারেট করা"""
        clean_text = audio_text.strip()
        if not clean_text:
            return
        print(f"Jarvis: {clean_text}")
        try:
            self.engine.say(clean_text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Speech engine runtime exception: {e}")

    def greet_user(self):
        """দিনের সময়ের ওপর ভিত্তি করে ইউজারকে সম্ভাষণ জানানো"""
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            self.speak("Good Morning!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("I am Jarvis. System protocols are online. How can I assist you today?")

    def take_command(self) -> str:
        """মাইক্রোফোন ইনপুট নিয়ে টেক্সটে কনভার্ট করা (মেমোরি সেফ)"""
        recognizer = sr.Recognizer()
        
        # পিসি-র ডিফল্ট অডিও সোর্স বাউন্ড চেক
        try:
            with sr.Microphone() as source:
                logger.info("Microphone capturing active ambient sound...")
                recognizer.pause_threshold = 1.0
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("\nListening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except Exception as mic_err:
            logger.error(f"Hardware Microphone is unreachable or muted: {mic_err}")
            return "none"

        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            return query.lower().strip()
        except sr.UnknownValueError:
            # কথা বুঝতে না পারলে ক্রাশ না করে গ্রেসফুলি হ্যান্ডেল করা
            logger.warning("Google Speech Recognition could not understand audio signature.")
            return "none"
        except sr.RequestError as req_err:
            logger.error(f"Network interface drop or API request failed: {req_err}")
            return "none"
        except Exception as e:
            logger.error(f"Unexpected recognition pipeline failure: {e}")
            return "none"

    def execute_pipeline(self):
        """ইউজার কমান্ড প্রসেস এবং এক্সেকিউশন লুপ"""
        self.greet_user()
        
        while True:
            query = self.take_command()
            
            if query == "none":
                continue

            # ১. উইকিপিডিয়া সার্চ মডিউল (ক্রাশ প্রটেকশন সহ)
            if 'wikipedia' in query:
                self.speak('Searching target database on Wikipedia...')
                search_query = query.replace("wikipedia", "").strip()
                if not search_query:
                    self.speak("What topic should I look up on Wikipedia?")
                    continue
                try:
                    # auto_suggest=False ব্যবহার করে Ambiguity Error ডিফেন্ড করা
                    results = wikipedia.summary(search_query, sentences=2, auto_suggest=False)
                    self.speak("According to structural records:")
                    self.speak(results)
                except wikipedia.exceptions.DisambiguationError as dis_err:
                    logger.warning(f"Ambiguous query context caught: {dis_err}")
                    self.speak("The topic matches multiple references. Please be more specific.")
                except wikipedia.exceptions.PageError:
                    self.speak("I am sorry, no page was discovered matching your statement.")
                except Exception as e:
                    logger.error(f"Wikipedia API failure: {e}")
                    self.speak("Internal error connection drop with Wikipedia node.")

            # ২. প্রোটোকল সেফ ব্রাউজার ওপেনিং
            elif 'open google' in query:
                self.speak("Opening Google.")
                webbrowser.open("https://www.google.com")

            elif 'open youtube' in query:
                self.speak("Opening YouTube.")
                webbrowser.open("https://www.youtube.com")

            # ৩. টাইম ডিসপ্লে ফরম্যাটিং
            elif 'the time' in query or 'current time' in query:
                str_time = datetime.datetime.now().strftime("%I:%M %p") # ১২ ঘণ্টার সুন্দর এএম/পিএম ফরম্যাট   
                self.speak(f"Sir, the system timestamp records {str_time}")

            # ৪. সিকিউর প্রসেস এক্সিকিউশন (Subprocess দিয়ে ফিক্স)
            elif 'open code' in query or 'vs code' in query:
                # ডাইনামিক এনভায়রনমেন্ট পাথ চেক (হার্ডকোডেড ইউজারনেম ডিফেন্স)
                local_app_data = os.getenv('LOCALAPPDATA')
                if local_app_data:
                    code_path = os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe")
                    
                    if os.path.exists(code_path):
                        self.speak("Launching Visual Studio Code interface.")
                        # os.startfile এর বদলে সিকিউর Popen অবজেক্ট ব্যবহার
                        subprocess.Popen([code_path])
                    else:
                        self.speak("VS Code binary file not found in default local path.")
                else:
                    self.speak("System local configuration path could not be resolved.")

            # ৫. গ্রেসফুল শাটডাউন
            elif any(token in query for token in ['offline', 'stop', 'quit', 'exit', 'goodbye']):
                self.speak("Deactivating system links. Moving Jarvis offline. Goodbye, Sir!")
                break

# =====================================================================
# SYSTEM MAIN ENTRY GUARD
# =====================================================================
if __name__ == "__main__":
    assistant = JarvisAssistant()
    try:
        assistant.execute_pipeline()
    except KeyboardInterrupt:
        logger.info("Force interrupt caught. Safely closing voice core loops.")
        sys.exit(0)
