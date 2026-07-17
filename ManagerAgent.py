import os
import pyttsx3
from gtts import gTTS

class TextToSpeechManager:
    def __init__(self, offline_mode: bool = True):
        """
        Initializes the TTS engine.
        :param offline_mode: If True, uses pyttsx3 (local/offline). If False, uses gTTS (online/natural).
        """
        self.offline_mode = offline_mode
        
        if self.offline_mode:
            # Initialize offline engine (pyttsx3)
            self.engine = pyttsx3.init()
            # Set default properties
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Set default voice (usually index 0 is male, 1 is female depending on the OS)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id) # Set to female voice if available

    def speak(self, text: str):
        """
        Pronounces the text immediately.
        """
        if not text:
            return

        print(f"[TTS Output]: {text}")
        
        if self.offline_mode:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            # Online mode (gTTS) - requires active internet connection
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                temp_filename = "temp_voice.mp3"
                tts.save(temp_filename)
                
                # Play the generated audio file
                # Note: Playsound or OS system calls might differ across Windows/Mac/Linux
                if os.name == 'nt': # Windows
                    os.system(f"start {temp_filename}")
                else: # Mac/Linux
                    os.system(f"afplay {temp_filename} || play {temp_filename}")
                    
            except Exception as e:
                print(f"[TTS Error]: Online TTS failed, falling back to local engine. Error: {e}")
                # Fallback to pyttsx3 offline
                fallback_engine = pyttsx3.init()
                fallback_engine.say(text)
                fallback_engine.runAndWait()

    def save_to_file(self, text: str, output_filepath: str):
        """
        Saves the spoken text into an audio file.
        """
        print(f"Saving speech audio to: {output_filepath}")
        if self.offline_mode:
            self.engine.save_to_file(text, output_filepath)
            self.engine.runAndWait()
        else:
            tts = gTTS(text=text, lang='en')
            tts.save(output_filepath)


# =====================================================================
# Demonstration & Integration Example
# =====================================================================
if __name__ == "__main__":
    # 1. Initialize local (offline) voice manager
    voice_system = TextToSpeechManager(offline_mode=True)
    
    # Let the system announce its status
    voice_system.speak("Initializing system. Provisioning 1000 AI Employee Agents under Manager David.")
    
    # 2. To save the announcement as an audio file
    # voice_system.save_to_file("Project HierarchAI successfully initiated.", "init_announcement.mp3")
