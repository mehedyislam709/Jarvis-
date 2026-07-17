import os
import sys
import re
import json
import logging
import requests
from urllib.parse import urlparse
import ipaddress
import socket
from typing import Dict, Any, Optional

# Programmatic Git Library Import with fail-safe error handling
try:
    import git
except ImportError:
    logging.critical("[Fatal Init] GitPython is missing. Execute 'pip install gitpython' to resolve.")
    sys.exit(1)

# Configure ultra-secure logging with standard out channels
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Jarvis Autonomous Core) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("jarvis_terminal_executor.log", encoding="utf-8")
    ]
)

class SecurityError(Exception):
    """Custom exception raised when structural execution violates core guardrails."""
    pass

# =====================================================================
#             MODULE 1: AUTO-GIT COMMIT AGENT (SECURE CORE)
# =====================================================================
class JarvisGitAgent:
    """
    Programmatic Git automation agent. Completely avoids raw system shell invocation
    to eliminate risk of command injection exploits.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.repo: Optional[git.Repo] = None
        self._initialize_repository()

    def _initialize_repository(self):
        """Validates and opens the local git repository programmatically."""
        try:
            self.repo = git.Repo(self.repo_path)
            if self.repo.bare:
                raise git.InvalidGitRepositoryError("Repository is bare.")
            logging.info(f"[Git Agent] Active repository connected securely at: {self.repo_path}")
        except git.InvalidGitRepositoryError:
            logging.error(f"[Git Agent] Fail: '{self.repo_path}' is not a valid Git repository.")
        except Exception as e:
            logging.critical(f"[Git Agent] Initialization Exception: {str(e)}")

    def commit_and_push_updates(self, commit_message: str, branch_name: str = "main") -> bool:
        """Tracks modified files, sanitizes commit messages, and pushes upstream securely."""
        if not self.repo:
            logging.error("[Git Agent] Action aborted: Repository connection is offline.")
            return False

        try:
            # 1. Programmatically verify changed or untracked file status first
            if not self.repo.is_dirty(untracked_files=True):
                logging.info("[Git Agent] Clean state. No modified files detected for stage.")
                return True

            # 2. Strict Sanitize Commit Message
            # Remove control sequences, quotes, backslashes, and prevent leading dashes (Flag Injection)
            clean_message = re.sub(r'[\r\n`"\'$\\;]', '', commit_message).strip()
            clean_message = clean_message.lstrip('-') 
            
            if not clean_message:
                clean_message = "Jarvis Auto-Commit: Maintenance and optimizations."

            # Strict branch validation to prevent Ref hijacking / Command injection via branch name
            if not re.match(r'^[a-zA-Z0-9_\-\./]+$', branch_name):
                raise SecurityError(f"Invalid branch name pattern: {branch_name}")

            logging.info("[Git Agent] Staging modified and untracked changes...")
            self.repo.git.add(A=True) 

            # 3. Perform commit
            logging.info(f"[Git Agent] Executing commit: '{clean_message}'")
            commit_object = self.repo.index.commit(clean_message)
            logging.info(f"[Git Agent] Commit successful. Hash: {commit_object.hexsha[:8]}")

            # 4. Programmatic Push securely passing target branch
            logging.info(f"[Git Agent] Initiating upstream push to branch: '{branch_name}'")
            origin = self.repo.remote(name="origin")
            
            # Explicit refspec tracking ensures exact push target and prevents branch hijacking
            push_info_list = origin.push(refspec=f"refs/heads/{branch_name}:refs/heads/{branch_name}")
            
            # Evaluate remote push feedback codes
            for push_info in push_info_list:
                if push_info.flags & git.remote.PushInfo.ERROR:
                    logging.error(f"[Git Agent] Push Rejected or Failed. Summary: {push_info.summary}")
                    return False

            logging.info("[Git Agent] Upstream sync accomplished without errors.")
            return True

        except SecurityError as sec_err:
            logging.critical(f"[Git Agent] Security Restriction: {sec_err}")
            return False
        except git.GitCommandError as git_err:
            logging.error(f"[Git Agent] Git command engine error: {git_err.stderr or git_err}")
            return False
        except Exception as general_err:
            logging.critical(f"[Git Agent] System processing fault: {str(general_err)}")
            return False


# =====================================================================
#             MODULE 2: SECURE API COMMAND GENERATOR & CALLER
# =====================================================================
class JarvisAPIGenerator:
    """
    Constructs and executes REST API requests safely. Bypasses curl command-line
    utility execution and prevents SSRF vulnerabilities.
    """
    def __init__(self):
        self.allowed_methods = {"GET", "POST", "PUT", "DELETE"}
        self.session = requests.Session() # Reuse connection pools securely

    def validate_url(self, url: str) -> str:
        """Enforces strictly secure HTTPS layers and blocks SSRF (Local/Private IPs)."""
        clean_url = url.strip()
        parsed_url = urlparse(clean_url)

        if parsed_url.scheme != "https":
            raise SecurityError("Unsafe protocol detected! This system operates on 'https://' only.")
        
        hostname = parsed_url.hostname
        if not hostname:
            raise SecurityError("Invalid URL target endpoint.")

        # Prevent SSRF (Server-Side Request Forgery) by resolving IP and blocking private ranges
        try:
            ip_address_resolved = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_address_resolved)
            
            if ip_obj.is_private or ip_obj.is_loopback:
                raise SecurityError(f"Access to private/local network blocked: {ip_address_resolved}")
        except socket.gaierror:
            raise SecurityError(f"Could not resolve domain host: {hostname}")
        except ValueError:
            raise SecurityError("Invalid IP structure detected during resolution.")

        return clean_url

    def execute_api_call(self, method: str, url: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        """Runs the programmatically assembled API request inside a strict safety sandbox."""
        upper_method = method.upper()
        if upper_method not in self.allowed_methods:
            logging.error(f"[API Core] Blocked: Request method '{upper_method}' is not allowed.")
            return None

        try:
            secure_url = self.validate_url(url)
            logging.info(f"[API Core] Safely calling API [{upper_method}] to resource: {secure_url}")

            # Enforce explicit configurations (10s timeout, max 3 redirects to prevent loops)
            response = self.session.request(
                method=upper_method,
                url=secure_url,
                headers=headers,
                json=payload if upper_method in {"POST", "PUT"} else None,
                params=payload if upper_method == "GET" else None,
                timeout=10,
                allow_redirects=True
            )

            logging.info(f"[API Core] Request complete. Response Code: {response.status_code}")
            return response

        except SecurityError as sec_err:
            logging.critical(f"[API Core] Security Breach Flagged: {sec_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            logging.error(f"[API Core] Connection transmission error: {req_err}")
            return None


# =====================================================================
#             CORE TERMINAL SYSTEM: INTEGRATED PLATFORM
# =====================================================================
class JarvisTerminalPlatform:
    def __init__(self):
        self.git_agent = JarvisGitAgent()
        self.api_generator = JarvisAPIGenerator()

    def run(self):
        """Operations portal for Git and API Automation."""
        while True:
            print("\n" + "█"*65)
            print("         JARVIS AUTONOMOUS TERMINAL EXECUTOR: PRODUCTION        ")
            print("█"*65)
            print("1. Stage, Auto-Commit and Push Changes")
            print("2. Safe API Request Builder & Executor")
            print("3. Emergency System Lockout")
            print("-" * 65)

            choice = input("Select Operation Index (1-3): ").strip()

            if choice == '1':
                msg = input("\nEnter Git commit message: ").strip()
                branch = input("Target branch (default: main): ").strip() or "main"
                if msg:
                    print("\n[Jarvis Autonomous] Validating code changes and staging...")
                    success = self.git_agent.commit_and_push_updates(msg, branch)
                    if success:
                        print("\n[Jarvis Autonomous] Git repository synchronized perfectly.")
                    else:
                        print("\n[Jarvis Autonomous] Sync operation aborted. Check logs.")

            elif choice == '2':
                method = input("\nHTTP Method (GET, POST, PUT, DELETE): ").strip()
                url = input("Destination HTTPS Endpoint: ").strip()
                headers_input = input("Enter Headers (JSON format or leave empty): ").strip()
                payload_input = input("Enter Payload Data (JSON format or leave empty): ").strip()

                headers = None
                payload = None

                try:
                    if headers_input:
                        headers = json.loads(headers_input)
                    if payload_input:
                        payload = json.loads(payload_input)
                except Exception as json_err:
                    print(f"\n[Syntax Error] Invalid JSON string provided: {json_err}")
                    continue

                if method and url:
                    print("\n[Jarvis Autonomous] Running API validation layers...")
                    resp = self.api_generator.execute_api_call(method, url, payload, headers)
                    if resp is not None:
                        print(f"\n--- API RESPONSE [STATUS: {resp.status_code}] ---")
                        try:
                            print(json.dumps(resp.json(), indent=2))
                        except ValueError:
                            print(resp.text)

            elif choice == '3':
                print("\nInitiating terminal controller lockdown... Goodbye.")
                break


if __name__ == "__main__":
    mainframe = JarvisTerminalPlatform()
    mainframe.run()
