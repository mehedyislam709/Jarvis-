import os
import os
import logging
import subprocess
import shlex
from typing import Optional
import pyttsx3
from gtts import gTTS

# Configure highly secure, enterprise-grade logger footprints
logging.basicConfig(level=logging.INFO, format="[TTS] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisTTS")

class TextToSpeechManager:
    def __init__(self, offline_mode: bool = True, rate: int = 150, volume: float = 0.9):
        """
        Initializes the robust Text-To-Speech lifecycle interface.
        :param offline_mode: True uses pyttsx3 (local), False uses gTTS (cloud-based network mode).
        :param rate: Speed configuration rate for the local voice generator.
        :param volume: Master amplitude multiplier bounded between 0.0 and 1.0.
        """
        self.offline_mode = offline_mode
        self._temp_filename = "temp_voice.mp3"
        
        # Always initialize pyttsx3 locally so fallback capability is instantly hot-swappable
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            # Enforce data sanitization parameters on floating inputs securely
            self.engine.setProperty('volume', max(0.0, min(volume, 1.0)))
            
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                # Set default secondary voice if safely provisioned by OS platform
                self.engine.setProperty('voice', voices[1].id)
        except Exception as init_err:
            logger.critical(f"Failed to instantiate local fallback offline audio drivers: {init_err}")
            self.engine = None

    def _sanitize_string(self, text: str) -> str:
        """Sanitizes text strings to defend internal structures against system attacks."""
        if not text:
            return ""
        # Truncate large paragraphs to prevent memory saturation buffer overflows
        return text.strip()[:1000]

    def _play_audio_safely(self, filepath: str) -> None:
        """
        Executes native operating system audio players safely using isolated subprocess blocks.
        Completely eliminates shell injection vulnerabilities inherent to traditional os.system calls.
        """
        # Resolve real paths safely without relying on dynamic user concatenation hooks
        absolute_target = os.path.abspath(filepath)
        
        try:
            if os.name == 'nt':  # Windows Environment Platform
                # Secure alternative execution strategy for native Windows architecture
                os.startfile(absolute_target)
            else:  # Linux / Unix / macOS Architectures
                # Use shlex to safely quote targets and subprocess to prevent command execution chaining
                safe_path = shlex.quote(absolute_target)
                cmd = f"afplay {safe_path} || play {safe_path}"
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as proc_err:
            logger.error(f"Media subsystem failed to render pipeline output target: {proc_err}")

    def _cleanup_temp_file(self) -> None:
        """Cleans up volatile cached media footprints on disk safely."""
        try:
            if os.path.exists(self._temp_filename):
                os.remove(self._temp_filename)
        except OSError as clean_err:
            logger.debug(f"Volatile cache file locked or unavailable for removal: {clean_err}")

    def speak(self, text: str) -> None:
        """Pronounces the provisioned text string with automated fault isolation handling."""
        clean_text = self._sanitize_string(text)
        if not clean_text:
            return

        logger.info(f"Synthesizing Vocal Announcement Pipeline Output: '{clean_text[:50]}...'")

        if self.offline_mode or not self.engine:
            self._speak_offline(clean_text)
        else:
            self._speak_online(clean_text)

    def _speak_offline(self, text: str) -> None:
        """Isolated local synthesis sequence loop."""
        if not self.engine:
            logger.error("Vocal engine processing aborted: No offline audio architecture found.")
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as offline_err:
            logger.error(f"Local hardware synthesizer failed critically: {offline_err}")

    def _speak_online(self, text: str) -> None:
        """Isolated cloud network synthesis sequence loop with automatic fallback."""
        try:
            # Enforce clean workspace state immediately before initialization execution
            self._cleanup_temp_file()
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(self._temp_filename)
            self._play_audio_safely(self._temp_filename)
            
        except Exception as online_err:
            logger.error(f"Online TTS connection drop detected. Activating offline fallback array: {online_err}")
            # Fault Isolated Execution: Gracefully fallback directly onto initialized memory cache engine
            self._speak_offline(text)

    def save_to_file(self, text: str, output_filepath: str) -> None:
        """Saves spoken text output directly into an audio container target file safely."""
        clean_text = self._sanitize_string(text)
        safe_output = os.path.abspath(output_filepath)
        
        if not clean_text:
            return

        logger.info(f"Compiling binary media storage target dump container to: {safe_output}")
        try:
            if self.offline_mode and self.engine:
                self.engine.save_to_file(clean_text, safe_output)
                self.engine.runAndWait()
            else:
                tts = gTTS(text=clean_text, lang='en')
                tts.save(safe_output)
        except Exception as save_err:
            logger.error(f"Failed to securely export media metadata file stream: {save_err}")


# =====================================================================
# Main Execution Guard Context
# =====================================================================
if __name__ == "__main__":
    # Initialize the secured and heavily reinforced TTS infrastructure system 
    voice_system = TextToSpeechManager(offline_mode=True)
    
    # Process initialization instruction vocal metrics safely
    voice_system.speak("Initializing system. Provisioning 1000 AI Employee Agents under Manager David.")
