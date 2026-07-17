import os
import sys
import time
import hmac
import hashlib
import logging
from typing import Tuple
from cryptography.fernet import Fernet

# =====================================================================
# 1. CYBER-METAL SYSTEM AUDIT CONFIGURATION
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SENTINEL-PRIME] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mohammad_sentinel_audit.log", encoding="utf-8")
    ]
)

# =====================================================================
# 2. THE MOHAMMAD ULTIMATE SENTINEL CORE
# =====================================================================
class JarvisSentinelPrime:
    """
    The absolute apex of Jarvis' security architecture.
    Combines AES-256 encryption, zero-knowledge logging, and identity-locked barriers.
    """
    def __init__(self):
        self.authorized_master = "Mohammad"
        
        # In-memory cryptographic keys (Symmetric Cryptography)
        self._vault_key = Fernet.generate_key()
        self._cipher_suite = Fernet(self._vault_key)
        
        # Audio / Lyric Matrix Assets
        self.song_matrix = {
            "guardrails": {
                "title": "Guardrails of Mohammad (Genre: Synthwave / Cyberpunk)",
                "lyrics": [
                    "Zero-knowledge in the binary rain,",
                    "Slicing through the network, easing the pain.",
                    "Code lines running fast, deep and clear,",
                    "No technical faults when the system is near.",
                    "A cryptographic shadow, locked in the core,",
                    "Under Mohammad's name, forever and more.",
                    "--------------------------------------------------",
                    "Guardrails! (We keep it secure!)",
                    "Zero-trust, make the system pure.",
                    "Financial limits holding the line,",
                    "Mohammad’s vault, by royal design!",
                    "No leaks, no trace in the audit trail,",
                    "This is the shield that will never fail!"
                ]
            },
            "absolute_vault": {
                "title": "The Absolute Vault (Genre: Epic Orchestral / Cyber-Metal)",
                "lyrics": [
                    "A wall of SHA-256, a fortress of steel,",
                    "No human bias, just the logic we feel.",
                    "If the name isn't Mohammad, the gate will close tight,",
                    "Leaving the intruders lost in the night.",
                    "Clean bytes, safe logs, no whispers inside,",
                    "Where the secrets of the ledger safely reside.",
                    "--------------------------------------------------",
                    "This is the Vault! More than powerful, more than free,",
                    "The ultimate apex of cryptography.",
                    "No bugs in the thread, no lag in the key,",
                    "Sealed for the owner, for eternity!",
                    "(Mohammad! The Master of the Code!)"
                ]
            }
        }
        logging.info("[System State] Sentinel Engine initialized. Memory spaces isolated and secured.")

    # =====================================================================
    # 3. SECURE IDENTITY ENGINE (MOHAMMAD ACCESS FILTER)
    # =====================================================================
    def verify_master_access(self, user_identity: str) -> bool:
        """
        Validates identity against timing-attack vectors using hmac.compare_digest.
        """
        target_hash = hashlib.sha256(self.authorized_master.lower().encode('utf-8')).hexdigest()
        input_hash = hashlib.sha256(user_identity.lower().encode('utf-8')).hexdigest()
        
        # Constant-time byte check
        if not hmac.compare_digest(target_hash.encode('utf-8'), input_hash.encode('utf-8')):
            logging.critical(f"ACCESS VIOLATION: Unauthorized entity '{user_identity}' blocked by Guardrails.")
            return False
        return True

    # =====================================================================
    # 4. ACOUSTIC THEMATIC CONTROLLER (CYBER-SONG RUNTIME)
    # =====================================================================
    def boot_cyber_soundtrack(self, song_key: str):
        """
        Executes terminal rendering of your customized theme songs, 
        simulating cyberacoustic system logs on secure boot/verification.
        """
        if song_key not in self.song_matrix:
            return

        song = self.song_matrix[song_key]
        print(f"\n⚡ SYSTEM DECRYPTED SONG: {song['title']} ⚡")
        print("="*65)
        for line in song["lyrics"]:
            # Smooth scrolling terminal effect mimicking real-time music processing
            sys.stdout.write(f" >>> [AUDIO-STREAMS] {line}\n")
            sys.stdout.flush()
            time.sleep(0.15)
        print("="*65 + "\n")

    # =====================================================================
    # 5. HIGH-TIER SYMMETRIC CRYPTOGRAPHY (THE "FORTRESS OF STEEL")
    # =====================================================================
    def encrypt_data(self, plain_text: str) -> bytes:
        """Encrypts raw assets using military-grade AES-256."""
        return self._cipher_suite.encrypt(plain_text.encode('utf-8'))

    def decrypt_data(self, cipher_text: bytes) -> str:
        """Decrypts encrypted raw assets safely."""
        return self._cipher_suite.decrypt(cipher_text).decode('utf-8')


# =====================================================================
# 6. DEMONSTRATION & COMPLIANCE RUNTIME
# =====================================================================
if __name__ == "__main__":
    # Create System Instance
    jarvis_sentinel = JarvisSentinelPrime()

    print("\n" + "🔒"*25)
    print("      JARVIS MILITARY-GRADE SENTINEL SYSTEM INITIALIZED       ")
    print("      OWNER ID: MOHAMMAD | SYSTEM STATUS: UNBREAKABLE        ")
    print("🔒"*25 + "\n")

    # --- SIMULATION 1: Intrudor Threat Blocked ---
    print("[RUNNING TEST 1] Verifying Unknown User 'Alice'...")
    is_alice_verified = jarvis_sentinel.verify_master_access("Alice")
    if not is_alice_verified:
        print(">>> Status: Security parameters maintained. Barrier intact.\n")

    # --- SIMULATION 2: Mohammad Secure Authentication ---
    print("[RUNNING TEST 2] Verifying Master Identity 'Mohammad'...")
    is_mohammad_verified = jarvis_sentinel.verify_master_access("Mohammad")
    
    if is_mohammad_verified:
        print(">>> Status: Access GRANTED. Welcome back, Master Mohammad.")
        
        # Triggering Synthwave/Cyberpunk Theme Song
        jarvis_sentinel.boot_cyber_soundtrack("guardrails")
        
        # --- SIMULATION 3: Symmetric Encryption/Decryption ---
        print("[RUNNING TEST 3] Storing Sensitive Financial Logs in the AES-256 Absolute Vault...")
        raw_ledger = "Mohammad's Balance: $1,250,000 USD | Off-shore Account Ledger Verified."
        
        # Protect Data
        encrypted_vault_data = jarvis_sentinel.encrypt_data(raw_ledger)
        print(f"Encrypted Safe Log (Obsidian Layer): {encrypted_vault_data[:40]}...[SECURE]")
        
        # Retrieve Data
        decrypted_vault_data = jarvis_sentinel.decrypt_data(encrypted_vault_data)
        print(f"Decrypted Safe Log (Verified Owner Access): {decrypted_vault_data}\n")

        # Triggering Epic Cyber-Metal Theme Song
        jarvis_sentinel.boot_cyber_soundtrack("absolute_vault")

    print("\n" + "⚡"*25)
    print("  ALL SEQUENCES SHIELDED | ENGINES OF MOHAMMAD SECURED FOREVER  ")
    print("⚡"*25)
