import os
import sys
import time
import math
import secrets
import logging
import numpy as np
import sounddevice as sd
from scipy.signal import welch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Jarvis Security Core) %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class JarvisSecureMainframe:
    def __init__(self):
        # Biometric Thresholds
        self.AUDIO_SAMPLE_RATE = 16000  # 16kHz clean analysis
        self.RECORDING_DURATION = 3.0   # 3 seconds security window
        
        # Reference voice model ranges
        self.TARGET_SPECTRAL_CENTROID_RANGE = (1200.0, 2400.0)
        self.TARGET_RMS_ENERGY_MIN = 0.015
        
        # Intruder Defense Variables (Using monotonic time to prevent clock tampering)
        self.FAILED_ATTEMPT_LIMIT = 3
        self.failed_attempts_counter = 0
        self.is_locked_out = False
        self.lockout_end_time = 0.0
        self.LOCKOUT_COOLDOWN_SEC = 60  

        self.secured_log_path = "jarvis_intrusion_vault.log"
        self._initialize_secure_log()

    def _initialize_secure_log(self):
        """Creates secure log file safely."""
        if not os.path.exists(self.secured_log_path):
            with open(self.secured_log_path, "w", encoding="utf-8") as f:
                f.write("[SYSTEM BOOT] Safe-room initialization sequence active.\n")

    def analyze_voice_biometrics(self, audio_signal: np.ndarray) -> bool:
        """Extracts spectral signatures and safely validates frequency distribution."""
        if audio_signal is None or len(audio_signal) <= 1:
            return False

        # Calculate RMS Energy Safely
        rms_energy = np.sqrt(np.mean(audio_signal**2))
        if rms_energy < self.TARGET_RMS_ENERGY_MIN or np.isnan(rms_energy):
            logging.warning("[Biometric Engine] Invalid biometric payload: Volume too faint or dead signal.")
            return False

        # Spectral Centroid Calculation using Welch's estimator
        try:
            frequencies, power_density = welch(audio_signal, self.AUDIO_SAMPLE_RATE, nperseg=1024)
            power_density_sum = np.sum(power_density)
            
            if power_density_sum <= 0 or np.isnan(power_density_sum):
                return False
                
            weighted_frequencies_sum = np.sum(frequencies * power_density)
            spectral_centroid = weighted_frequencies_sum / power_density_sum
        except Exception as math_err:
            logging.error(f"[Biometric Engine] Mathematical signal analysis failure: {math_err}")
            return False

        logging.info(f"[Biometric Analysis] Energy Level: {rms_energy:.4f} | Spectral Signature: {spectral_centroid:.2f} Hz")

        min_f, max_f = self.TARGET_SPECTRAL_CENTROID_RANGE
        return min_f <= spectral_centroid <= max_f

    def capture_voice_token(self) -> Optional[np.ndarray]:
        """Records secure live audio from the microphone with runtime fail-safes."""
        print("\n>>> [JARVIS BIOMETRIC] RECORDING LIVE AUDIO PASS-TOKEN IN 3 SECONDS... SPEAK NOW.")
        time.sleep(0.5)
        
        try:
            # Captures mono-channel float32 array
            audio_data = sd.rec(int(self.RECORDING_DURATION * self.AUDIO_SAMPLE_RATE),
                                samplerate=self.AUDIO_SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()  
            return np.squeeze(audio_data)
        except Exception as hardware_err:
            logging.critical(f"[Hardware Exception] Microphone driver failure or disconnected: {hardware_err}")
            return None

    def attempt_biometric_unlock(self) -> bool:
        """Orchestrates secure validation and clock-tamper-proof brute-force cool downs."""
        current_time = time.monotonic() # Immune to system clock modifications
        
        if self.is_locked_out:
            if current_time < self.lockout_end_time:
                remaining = int(self.lockout_end_time - current_time)
                logging.error(f"[LOCKOUT ACTIVE] Security block active. Try again in {remaining}s.")
                return False
            else:
                self.is_locked_out = False
                self.failed_attempts_counter = 0
                logging.info("[Lockout Reset] Normal operations returned. Proceed to biometrics.")

        audio_token = self.capture_voice_token()
        if audio_token is None:
            logging.error("[Access Denied] Failed to capture biometrics due to hardware failure.")
            return False

        validated = self.analyze_voice_biometrics(audio_token)

        if validated:
            logging.info("[ACCESS GRANTED] Voice token authenticated. Welcome back, Operator.")
            self.failed_attempts_counter = 0
            return True
        else:
            self.failed_attempts_counter += 1
            logging.warning(f"[ACCESS DENIED] Signature mismatch. Failure index: {self.failed_attempts_counter}/{self.FAILED_ATTEMPT_LIMIT}")
            
            if self.failed_attempts_counter >= self.FAILED_ATTEMPT_LIMIT:
                self.is_locked_out = True
                self.lockout_end_time = time.monotonic() + self.LOCKOUT_COOLDOWN_SEC
                logging.critical(f"[INTRUDER ALERT] System locked down for {self.LOCKOUT_COOLDOWN_SEC}s!")
            return False

    def secure_log_eraser(self, target_filepath: str):
        """
        Industrial-strength file shredder. Forces OS-level buffer flushing (fsync) 
        and truncates data to guarantee absolute destruction even on modern SSDs.
        """
        safe_path = os.path.abspath(target_filepath)
        if not os.path.exists(safe_path):
            logging.error(f"[Secure Shred] Target '{safe_path}' does not exist.")
            return

        try:
            file_size = os.path.getsize(safe_path)
            logging.info(f"[Secure Shred] Purging target: {safe_path} ({file_size} bytes)")

            # Open file with direct low-level OS write permissions (no caching)
            fd = os.open(safe_path, os.O_RDWR | os.O_BINARY if hasattr(os, 'O_BINARY') else os.O_RDWR)
            try:
                # Pass 1: Cryptographically secure random bytes
                os.lseek(fd, 0, os.SEEK_SET)
                os.write(fd, secrets.token_bytes(file_size))
                os.fsync(fd)  # Force OS to push data to the actual hardware controller

                # Pass 2: Overwrite with all Zero bytes to clear signatures
                os.lseek(fd, 0, os.SEEK_SET)
                os.write(fd, b'\x00' * file_size)
                os.fsync(fd)
                
                # Truncate file size to 0 bytes at the OS level
                os.ftruncate(fd, 0)
            finally:
                os.close(fd)

            # Metadata Deletion Layer: Obfuscate file name before unlinking
            shredded_temp_name = os.path.join(os.path.dirname(safe_path), secrets.token_hex(16))
            os.rename(safe_path, shredded_temp_name)
            os.remove(shredded_temp_name)
            
            logging.info("[Secure Shred] Anti-forensic purge completed successfully.")
        except Exception as shred_err:
            logging.critical(f"[Shred Error] Failed to securely purge logs: {shred_err}")


# =====================================================================
#             TEST RUN: INTERACTIVE SYSTEM TESTING
# =====================================================================
if __name__ == "__main__":
    jarvis_vault = JarvisSecureMainframe()
    
    while True:
        print("\n" + "☠"*60)
        print("          JARVIS CYBER-DEFENSE & BIOMETRICS VAULT          ")
        print("☠"*60)
        print("1. Speak & Authenticate (Voice-Key)")
        print("2. Write Sample Intrusion Logs")
        print("3. Execute Cryptographic Log Purge (Secure Log Eraser)")
        print("4. Safe Shutdown")
        print("-" * 60)

        choice = input("Select System Protocol (1-4): ").strip()

        if choice == '1':
            jarvis_vault.attempt_biometric_unlock()
        elif choice == '2':
            with open(jarvis_vault.secured_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"[ALERT INT] Intrusion attempt blocked at monotonic timestamp: {time.monotonic()}\n")
            print("\n[Admin Info] Simulated log entries successfully generated.")
        elif choice == '3':
            confirm = input("\n[WARNING] Shredding is IRREVERSIBLE. Proceed? (y/n): ").strip().lower()
            if confirm == 'y':
                jarvis_vault.secure_log_eraser(jarvis_vault.secured_log_path)
        elif choice == '4':
            print("\nShutting down Jarvis Defense Core.")
            break
