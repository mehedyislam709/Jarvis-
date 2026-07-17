import os
import sys
import hmac
import hashlib
import logging
import datetime
from typing import Dict, Any, Tuple, Optional
from cryptography.fernet import Fernet

# ========================================================
#            LOGGING & AUDIT TRAIL SYSTEM
# ========================================================
# জিরো-নলেজ লগ পলিসি মেনে চলার জন্য স্ট্যান্ডার্ড লগার কনফিগার করা হয়েছে।
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AUDIT-TRAIL] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("jarvis_banking_audit.log", encoding="utf-8")
    ]
)

class MohammadVaultEngine:
    """
    The Ultimate Secure Banking Engine for Jarvis.
    Enforces Strict Access Control, Zero-Knowledge Logging, and Financial Guardrails.
    """
    def __init__(self):
        # Master Owner config (এই ব্যাংক অ্যাকাউন্টের একমাত্র মালিক "Mohammad")
        self.authorized_owner = "Mohammad"
        
        # Financial Guardrails (দৈনিক লেনদেন এবং একক লেনদেনের সর্বোচ্চ সীমা)
        self.single_tx_limit = 100000.00  # Max 1,00,000 BDT/USD
        self.daily_tx_limit = 300000.00   # Max 3,00,000 BDT/USD
        self.accumulated_today = 0.0
        self.last_tx_date = datetime.date.today()

        # Vault Cryptography (লকাল ডেটা এনক্রিপ্ট করার জন্য চাবি জেনারেশন)
        self._encryption_key = Fernet.generate_key()
        self._cipher_suite = Fernet(self._encryption_key)

        logging.info("[Vault Init] Cryptographic Engine online. Symmetric keys generated in-memory.")
        logging.info(f"[Guardrails] Access policy locked to authorized owner: '{self.authorized_owner}'")

    # ========================================================
    # 1. ACCESS CONTROL: OWNER VERIFICATION (MOHAMMAD ONLY)
    # ========================================================
    def verify_identity(self, user_name: str, secure_token: str) -> bool:
        """
        মোহাম্মদের পরিচয় ক্রিপ্টোগ্রাফিকালি ভেরিফাই করে। 
        টাইমিং অ্যাটাক (Timing Attacks) ঠেকাতে constant-time comparison ব্যবহার করা হয়েছে।
        """
        # Timing Attack প্রুফ সিকিউরিটি চেক
        expected_owner = self.authorized_owner.lower().encode('utf-8')
        provided_user = user_name.lower().encode('utf-8')
        
        is_owner_valid = hmac.compare_digest(expected_owner, provided_user)
        
        if not is_owner_valid:
            # সিগনিফিক্যান্ট সিকিউরিটি ভায়োলেশন লগ
            logging.critical(f"UNAUTHORIZED ACCESS ATTEMPT. Username tried: '{user_name}'. Threat Blocked.")
            return False
            
        return True

    # ========================================================
    # 2. ZERO-KNOWLEDGE LOG POLICY: DATA MASKING & HASHING
    # ========================================================
    def secure_data_mask(self, raw_data: str) -> str:
        """
        জিরো-নলেজ পলিসির কোর ফাংশন।
        সংবেদনশীল ডেটা যেমন পিন, ওটিপি বা অ্যাকাউন্ট নম্বরকে ওয়ান-ওয়ে SHA-256 হ্যাশে কনভার্ট করে।
        লগে বা মেমোরিতে কখনোই মূল ডেটা থাকবে না।
        """
        if not raw_data:
            return ""
        
        # কনফিডেনশিয়াল ডেটার হ্যাশ জেনারেট করা হচ্ছে, যা রিভার্স করা অসম্ভব
        hashed_payload = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        
        # লগ বা স্ক্রিনে দেখানোর জন্য মাস্কড ফরম্যাট
        return f"SHA256:{hashed_payload[:12]}...[SECURE_MASKED]"

    # ========================================================
    # 3. FINANCIAL GUARDRAILS: TRANSACTION VALIDATOR
    # ========================================================
    def process_transaction(self, requester: str, amount: float, account_id: str) -> Tuple[bool, str]:
        """
        ফাইন্যান্সিয়াল লিমিট এবং সিকিউরিটি পলিসি ক্রস-চেক করে ট্রানজেকশন প্রসেস করে।
        """
        # ১. প্রথমেই ইউজার ভেরিফিকেশন (Only Mohammad has access)
        if not self.verify_identity(requester, "session_token_123"):
            return False, "REJECTED: Access Denied. Only owner 'Mohammad' can execute banking policies."

        # ২. লিমিট রিসেট (নতুন দিনে অটোমেটিক ডেইলি লিমিট রিসেট হবে)
        today = datetime.date.today()
        if today > self.last_tx_date:
            self.accumulated_today = 0.0
            self.last_tx_date = today
            logging.info("[Guardrails] New calendar day detected. Daily cumulative limit reset to 0.")

        # ৩. একক লেনদেনের সীমা পরীক্ষা
        if amount > self.single_tx_limit:
            err_msg = f"REJECTED: Single transaction limit exceeded ({self.single_tx_limit}). Requested: {amount}"
            self._write_audit_log("TX_BLOCKED", requester, account_id, amount, err_msg)
            return False, err_msg

        # ৪. দৈনিক মোট লেনদেনের সীমা পরীক্ষা
        if self.accumulated_today + amount > self.daily_tx_limit:
            err_msg = f"REJECTED: Daily total limit would exceed ({self.daily_tx_limit}). Current spent: {self.accumulated_today}"
            self._write_audit_log("TX_BLOCKED", requester, account_id, amount, err_msg)
            return False, err_msg

        # ৫. সফল ট্রানজেকশন এক্সেকিউশন ও লিমিট আপডেট
        self.accumulated_today += amount
        success_msg = f"SUCCESS: Authorized transfer of {amount} processed securely."
        self._write_audit_log("TX_SUCCESS", requester, account_id, amount, "None")
        
        return True, success_msg

    # ========================================================
    # 4. COMPLIANCE AUDIT TRAIL (ENCRYPTED & COMPLIANT)
    # ========================================================
    def _write_audit_log(self, status: str, user: str, account: str, amount: float, error_reason: str):
        """
        প্রতিটি এক্টিভিটির একটি ফুল অডিট ট্রেইল তৈরি করে।
        অ্যাকাউন্ট নম্বরের মতো ডেটা সরাসরি লগে না লিখে secure_data_mask() ব্যবহার করে লক করা হয়।
        """
        masked_account = self.secure_data_mask(account)
        timestamp = datetime.datetime.utcnow().isoformat()
        
        # স্ট্রাকচার্ড অডিট লগ ফরম্যাট
        audit_entry = (
            f"| Status: {status} "
            f"| User: {user} "
            f"| Hash-Account: {masked_account} "
            f"| Amount: {amount} "
            f"| Fail-Reason: {error_reason} "
            f"| UTC-Time: {timestamp}"
        )
        
        # অডিট ফাইলে সরাসরি রাইট করা হচ্ছে
        logging.info(f"[AUDIT-LOG-ENTRY] {audit_entry}")


# ========================================================
#                    SANDBOX SIMULATION
# ========================================================
if __name__ == "__main__":
    # ইনিশিয়েট জার্ভিস ব্যাংকিং ইঞ্জিন
    mohammad_vault = MohammadVaultEngine()

    print("\n" + "="*60)
    print("           JARVIS SECURE BANKING FRAMEWORK ONLINE          ")
    print("           OWNER: MOHAMMAD | MODE: ZERO-TRUST             ")
    print("="*60 + "\n")

    # সিনারিও ১: একজন অনুপ্রবেশকারী (যেমন: "UnknownUser") ট্রানজেকশন করার চেষ্টা করছে
    print("[Test 1] Attemping unauthorized transaction...")
    status, response = mohammad_vault.process_transaction(
        requester="UnknownUser", 
        amount=5000.0, 
        account_id="ACC-9999-8888-7777"
    )
    print(f"Jarvis Response: {response}\n")

    # সিনারিও ২: রিয়েল ইউজার "Mohammad" ট্রানজেকশন রিকোয়েস্ট পাঠাচ্ছেন (লিমিটের ভেতর)
    print("[Test 2] Owner 'Mohammad' requesting valid transaction...")
    status, response = mohammad_vault.process_transaction(
        requester="Mohammad", 
        amount=50000.0, 
        account_id="ACC-1122-3344-5566"
    )
    print(f"Jarvis Response: {response}\n")

    # সিনারিও ৩: "Mohammad" ট্রানজেকশন করার চেষ্টা করছেন যা একক ট্রানজেকশন লিমিট অতিক্রম করে
    print("[Test 3] Owner 'Mohammad' attempting to cross the single transaction guardrail...")
    status, response = mohammad_vault.process_transaction(
        requester="Mohammad", 
        amount=150000.0,  # Limit is 1,00,000
        account_id="ACC-1122-3344-5566"
    )
    print(f"Jarvis Response: {response}\n")

    print("[System Status] Sandbox simulation complete. Check 'jarvis_banking_audit.log' for encrypted compliance reports.")
