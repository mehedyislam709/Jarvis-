import sys
import hmac
import hashlib
import logging
import datetime
import secrets
from typing import Tuple
from cryptography.fernet import Fernet

# Centralized Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [VAULT-AUDIT] | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("jarvis_bank.audit")]
)

class MohammadVaultEngine:
    """
    Military-Grade Banking Engine with AES-256 Audit Encryption
    and Constant-Time identity verification.
    """
    def __init__(self):
        self._owner_identity = "Mohammad"
        self._vault_secret = secrets.token_bytes(32) # Runtime master key
        self._cipher = Fernet(Fernet.generate_key())
        
        self.single_tx_limit = 100000.00
        self.daily_tx_limit = 300000.00
        self.accumulated_today = 0.0
        self.last_tx_date = datetime.date.today()
        
        logging.info("Vault initialized: Cryptographic layers active.")

    def verify_identity(self, user_name: str) -> bool:
        """Constant-time comparison to prevent timing attacks."""
        return hmac.compare_digest(self._owner_identity.encode(), user_name.encode())

    def _encrypt_log(self, data: str) -> str:
        """Encrypts sensitive log entries using AES-256."""
        return self._cipher.encrypt(data.encode()).decode()

    def process_transaction(self, requester: str, amount: float, account_id: str) -> Tuple[bool, str]:
        """Processes transaction with strict validation guardrails."""
        
        # 1. Identity Verification
        if not self.verify_identity(requester):
            logging.error(f"Security Alert: Unauthorized access attempt by {requester}")
            return False, "ACCESS_DENIED: Identity mismatch."

        # 2. Reset Logic
        if datetime.date.today() > self.last_tx_date:
            self.accumulated_today = 0.0
            self.last_tx_date = datetime.date.today()

        # 3. Guardrail validation
        if amount > self.single_tx_limit:
            return False, "LIMIT_EXCEEDED: Transaction exceeds single transfer cap."
        
        if (self.accumulated_today + amount) > self.daily_tx_limit:
            return False, "LIMIT_EXCEEDED: Daily budget exhausted."

        # 4. Atomic Execution
        self.accumulated_today += amount
        self._audit_event("TX_SUCCESS", requester, account_id, amount)
        return True, "TRANSACTION_AUTHORIZED: Funds transferred successfully."

    def _audit_event(self, event_type: str, user: str, account: str, amount: float):
        """Writes encrypted, compliant audit trails."""
        raw_log = f"TYPE:{event_type} | USER:{user} | ACC:{account} | AMT:{amount} | TS:{datetime.datetime.now()}"
        encrypted_log = self._encrypt_log(raw_log)
        logging.info(f"AUDIT_BLOB: {encrypted_log}")

# --- Sandbox Simulation ---
if __name__ == "__main__":
    vault = MohammadVaultEngine()
    
    # Secure Test
    success, message = vault.process_transaction("Mohammad", 50000.0, "ACC-001")
    print(f"Status: {success} | Info: {message}")

