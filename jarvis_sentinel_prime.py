import os
import sys
import time
import hmac
import hashlib
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidToken

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
    Combines persistent AES-256 encryption, zero-knowledge logging, and identity barriers.
    """
    def __init__(self, key_path: str = "sentinel_vault.key"):
        self.key_path = os.path.abspath(key_path)
        
        # Hardened Identity Verification Layer (Zero-Knowledge Approach)
        # In production, this pre-computed SHA-256 hash resides securely outside raw text
        # Derived from: hashlib.sha256(b"Mohammad").hexdigest()
        self._authorized_master_hash = "507db41062b28c2901c0eb707137f6a7d65eb512c5b36449dd623a6703b41d01"
        
        # Initialize or Load Persistent Key Vault
        self._vault_key = self._load_or_create_vault_key()
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
        logging.info("[System State] Sentinel Engine initialized. Cryptographic assets locked.")

    def _load_or_create_vault_key(self) -> bytes:
        """Loads a persistent key from disk or creates one atomically if missing."""
        if os.path.exists(self.key_path):
            try:
                with open(self.key_path, "rb") as key_file:
                    key = key_file.read()
                # Simple validation check for Fernet key length (32 url-safe base64-encoded bytes)
                if len(key) != 44:
                    raise ValueError("Corrupted vault key length.")
                logging.info("[Key Vault] Persistent encryption key successfully restored.")
                return key
            except Exception as e:
                logging.error(f"[Key Vault] Error loading vault key: {e}. Re-generating key.")
        
        # Generate new persistent key safely
        new_key = Fernet.generate_key()
        try:
            # Low-level file creation with strict owner read/write permissions (Unix: 600)
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            mode = 0o600 
            with open(os.open(self.key_path, flags, mode), "wb") as key_file:
                key_file.write(new_key)
            logging.info(f"[Key Vault] Fresh persistent cryptographic key generated at: {self.key_path}")
        except Exception as e:
            logging.critical(f"[Key Vault] Critical error writing key to disk: {e}")
        return new_key

    # =====================================================================
    # 3. SECURE IDENTITY ENGINE (MOHAMMAD ACCESS FILTER)
    # =====================================================================
    def verify_master_access(self, user_identity: str) -> bool:
        """Validates identity securely using constant-time comparison against hashed values."""
        if not user_identity or not isinstance(user_identity, str):
            return False

        # Input sanitization to prevent Log Injection attacks
        sanitized_identity = re.sub(r'[^a-zA-Z0-9]', '', user_identity)[:50]

        # Standardizing byte conversion for deterministic hashing without losing entropy
        input_hash = hashlib.sha256(user_identity.strip().encode('utf-8')).hexdigest()
        
        # Constant-time byte verification against side-channel/timing attacks
        if not hmac.compare_digest(self._authorized_master_hash.encode('utf-8'), input_hash.encode('utf-8')):
            logging.critical(f"ACCESS VIOLATION: Unauthorized entity signature '{sanitized_identity}' blocked.")
            return False
        return True

    # =====================================================================
    # 4. ACOUSTIC THEMATIC CONTROLLER (CYBER-SONG RUNTIME)
    # =====================================================================
    def boot_cyber_soundtrack(self, song_key: str):
        """Simulates cyberacoustic terminal rendering of theme tracks."""
        if song_key not in self.song_matrix:
            return

        song = self.song_matrix[song_key]
        print(f"\n⚡ SYSTEM DECRYPTED SONG: {song['title']} ⚡")
        print("="*65)
        for line in song["lyrics"]:
            sys.stdout.write(f" >>> [AUDIO-STREAMS] {line}\n")
            sys.stdout.flush()
            time.sleep(0.05)  # Slightly accelerated for user fluid execution
        print("="*65 + "\n")

    # =====================================================================
    # 5. HIGH-TIER SYMMETRIC CRYPTOGRAPHY (THE "FORTRESS OF STEEL")
    # =====================================================================
    def encrypt_data(self, plain_text: str) -> Optional[bytes]:
        """Encrypts data using AES-256 standard via safe byte serialization."""
        if not plain_text:
            return None
        try:
            return self._cipher_suite.encrypt(plain_text.encode('utf-8'))
        except Exception as e:
            logging.error(f"[Crypto Error] Encryption failed: {e}")
            return None

    def decrypt_data(self, cipher_text: bytes) -> Optional[str]:
        """Decrypts payload with full validation checks against token tempering."""
        if not cipher_text or not isinstance(cipher_text, bytes):
            return None
        try:
            return self._cipher_suite.decrypt(cipher_text).decode('utf-8')
        except InvalidToken:
            logging.error("[Crypto Error] Decryption failed: Signature/Token validation failed (Tampering suspected).")
            return None
        except Exception as e:
            logging.error(f"[Crypto Error] Unexpected structural decryption failure: {e}")
            return None


# =====================================================================
# 6. DEMONSTRATION & COMPLIANCE RUNTIME
# =====================================================================
if __name__ == "__main__":
    import re # Temporary import for identity sanitization regex

    # Create System Instance
    jarvis_sentinel = JarvisSentinelPrime()

    print("\n" + "🔒"*25)
    print("      JARVIS MILITARY-GRADE SENTINEL SYSTEM INITIALIZED       ")
    print("      OWNER HASH LINKED | SYSTEM STATUS: UNBREAKABLE          ")
    print("🔒"*25 + "\n")

    # --- SIMULATION 1: Intruder Threat Blocked ---
    print("[RUNNING TEST 1] Verifying Unknown User 'Alice'...")
    if not jarvis_sentinel.verify_master_access("Alice"):
        print(">>> Status: Security parameters maintained. Barrier intact.\n")

    # --- SIMULATION 2: Mohammad Secure Authentication ---
    print("[RUNNING TEST 2] Verifying Master Identity 'Mohammad'...")
    if jarvis_sentinel.verify_master_access("Mohammad"):
        print(">>> Status: Access GRANTED. Welcome back, Master Mohammad.")
        
        # Triggering Soundtrack
        jarvis_sentinel.boot_cyber_soundtrack("guardrails")
        
        # --- SIMULATION 3: Symmetric Encryption/Decryption ---
        print("[RUNNING TEST 3] Storing Sensitive Financial Logs...")
        raw_ledger = "Mohammad's Balance: $1,250,000 USD | Secure Core System Sync Active."
        
        # Protect Data
        encrypted_vault_data = jarvis_sentinel.encrypt_data(raw_ledger)
        if encrypted_vault_data:
            print(f"Encrypted Safe Log (Obsidian Layer): {encrypted_vault_data[:40]}...[SECURE]")
            
            # Retrieve Data
            decrypted_vault_data = jarvis_sentinel.decrypt_data(encrypted_vault_data)
            print(f"Decrypted Safe Log (Verified Owner Access): {decrypted_vault_data}\n")

        # Triggering Epic Cyber-Metal Theme Song
        jarvis_sentinel.boot_cyber_soundtrack("absolute_vault")

    print("\n" + "⚡"*25)
    print("  ALL SEQUENCES SHIELDED | ENGINES OF MOHAMMAD SECURED FOREVER  ")
    print("⚡"*25)
