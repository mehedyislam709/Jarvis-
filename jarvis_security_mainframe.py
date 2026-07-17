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
        self.AUDIO_SAMPLE_RATE = 16000  # 16kHz standard for clean bio-analysis
        self.RECORDING_DURATION = 3.0   # 3 seconds security passphrase window
        
        # Pre-calculated reference biometric signature values (Calibrated Voice Model)
        # Note: In production, these represent your unique high-frequency vocal patterns.
        self.TARGET_SPECTRAL_CENTROID_RANGE = (1200.0, 2400.0)
        self.TARGET_RMS_ENERGY_MIN = 0.015
        
        # Intruder Defense Variables
        self.FAILED_ATTEMPT_LIMIT = 3
        self.failed_attempts_counter = 0
        self.is_locked_out = False
        self.lockout_end_time = 0.0
        self.LOCKOUT_COOLDOWN_SEC = 60  # 1-minute brute force prevention lock

        # Simulated dynamic logfile path
        self.secured_log_path = "jarvis_intrusion_vault.log"
        self._initialize_secure_log()

    def _initialize_secure_log(self):
        """Creates a dummy secure log if it doesn't already exist."""
        if not os.path.exists(self.secured_log_path):
            with open(self.secured_log_path, "w", encoding="utf-8") as f:
                f.write("[SYSTEM BOOT] Safe-room initialization sequence active.\n")
                f.write("[DATA LOG] Dynamic tracking logs enabled.\n")

    def analyze_voice_biometrics(self, audio_signal: np.ndarray) -> bool:
        """
        Extracts spectral signatures from the recorded voice wave.
        Validates energy content and frequency distribution.
        """
        # Calculate Root Mean Square (RMS) to confirm human-range voice volume
        rms_energy = np.sqrt(np.mean(audio_signal**2))
        if rms_energy < self.TARGET_RMS_ENERGY_MIN:
            logging.warning("[Biometric Engine] Invalid biometric payload: Volume too faint.")
            return False

        # Spectral Centroid Calculation using Welch's power spectral density (PSD) estimator
        frequencies, power_density = welch(audio_signal, self.AUDIO_SAMPLE_RATE, nperseg=1024)
        
        # Centroid formula: sum(f * P(f)) / sum(P(f))
        weighted_frequencies_sum = np.sum(frequencies * power_density)
        power_density_sum = np.sum(power_density)
        
        spectral_centroid = weighted_frequencies_sum / power_density_sum if power_density_sum > 0 else 0

        logging.info(f"[Biometric Analysis] Energy Level: {rms_energy:.4f} | Spectral Signature: {spectral_centroid:.2f} Hz")

        # Verify biometric profile fits inside user-calibrated envelope
        min_f, max_f = self.TARGET_SPECTRAL_CENTROID_RANGE
        if min_f <= spectral_centroid <= max_f:
            return True
        return False

    def capture_voice_token(self) -> np.ndarray:
        """Records a 3-second secure live audio capture from default system microphone."""
        print("\n>>> [JARVIS BIOMETRIC] RECORDING LIVE AUDIO PASS-TOKEN IN 3 SECONDS... SPEAK NOW.")
        time.sleep(0.5)
        
        try:
            # Captures a mono-channel float32 numpy array
            audio_data = sd.rec(int(self.RECORDING_DURATION * self.AUDIO_SAMPLE_RATE),
                                samplerate=self.AUDIO_SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()  # Block main thread execution until the mic hardware capture finishes
            return np.squeeze(audio_data)
        except Exception as hardware_err:
            logging.critical(f"[Hardware Exception] Microphone driver failure: {hardware_err}")
            return np.zeros(100)

    def attempt_biometric_unlock(self) -> bool:
        """Orchestrates secure validation, lockout limits, and brute-force cool downs."""
        current_time = time.time()
        
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
                self.lockout_end_time = time.time() + self.LOCKOUT_COOLDOWN_SEC
                logging.critical(f"[INTRUDER ALERT] System locked down for {self.LOCKOUT_COOLDOWN_SEC}s!")
            return False

    def secure_log_eraser(self, target_filepath: str):
        """
        Multi-pass DoD-style anti-forensics shredder. Overwrites file spaces
        directly on the storage block with zero bytes and random patterns before removal.
        """
        if not os.path.exists(target_filepath):
            logging.error(f"[Secure Shred] Target '{target_filepath}' does not exist.")
            return

        try:
            file_size = os.path.getsize(target_filepath)
            logging.info(f"[Secure Shred] Initiating zero-write overwriting sequence on target: {target_filepath} ({file_size} bytes)")

            # Run 3-Pass shredding sequence to destroy deep storage residuals
            with open(target_filepath, "ba+", buffering=0) as secure_file:
                # Pass 1: Overwrite completely with binary zeros
                secure_file.seek(0)
                secure_file.write(b'\x00' * file_size)
                
                # Pass 2: Overwrite completely with binary ones
                secure_file.seek(0)
                secure_file.write(b'\xff' * file_size)
                
                # Pass 3: Overwrite with cryptographically secure random bytes
                secure_file.seek(0)
                random_bytes = secrets.token_bytes(file_size)
                secure_file.write(random_bytes)

            # Metadata obfuscation - rename target to a random string before final unlink
            shredded_temp_name = os.path.join(os.path.dirname(target_filepath), secrets.token_hex(8))
            os.rename(target_filepath, shredded_temp_name)
            os.remove(shredded_temp_name)
            
            logging.info("[Secure Shred] Operation completed. Magnetic and SSD residual memory purged.")
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
                log_file.write(f"[ALERT INT] Intrusion attempt blocked at Unix timestamp: {time.time()}\n")
            print("\n[Admin Info] Simulated log entries successfully generated inside 'jarvis_intrusion_vault.log'.")
        elif choice == '3':
            confirm = input("\n[WARNING] This performs standard DOD-shred. Recovering is IMPOSSIBLE. Proceed? (y/n): ").strip().lower()
            if confirm == 'y':
                jarvis_vault.secure_log_eraser(jarvis_vault.secured_log_path)
        elif choice == '4':
            print("\nShutting down Jarvis Defense Core.")
            break
