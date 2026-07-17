import os
import logging
from typing import Optional, List, Dict
import openai
from openai import OpenAIError

# Configure enterprise-grade logging format
logging.basicConfig(level=logging.INFO, format="[Brain] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisBrain")

class AIConversationEngine:
    def __init__(self, model: str = "gpt-4o", max_history_turns: int = 10):
        """
        Initializes the hardened AI Conversation Engine.
        :param model: The target OpenAI model configuration string.
        :param max_history_turns: Maximum conversation turns to retain to prevent context window bloating.
        """
        # Security Fix: Never hardcode api keys. Load securely from environment variables.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.critical("Initialization aborted: 'OPENAI_API_KEY' environment variable is missing.")
            raise ValueError("Missing critical configuration credential setup.")
            
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_history_turns = max_history_turns
        
        # Core system instruction context setup
        self.system_instruction = {"role": "system", "content": "You are a helpful, witty coding assistant."}
        self.history: List[Dict[str, str]] = []

    def _sanitize_input(self, text: str) -> Optional[str]:
        """Validates and trims user input bounds securely."""
        if not text or not text.strip():
            logger.warning("Rejected input: Empty string payload received.")
            return None
        # Enforce text size safety ceiling (e.g., maximum 4000 characters) to mitigate DoS attacks
        return text.strip()[:4000]

    def _enforce_history_sliding_window(self) -> None:
        """
        Maintains a strict sliding window limit on chat history strings.
        Prevents unbounded token memory growth and financial pricing saturation exploits.
        """
        # Each turn consists of 2 entries (1 user message + 1 assistant reply)
        max_entries = self.max_history_turns * 2
        if len(self.history) > max_entries:
            # Drop the oldest user-assistant turn pairs while preserving the window capacity
            self.history = self.history[-max_entries:]

    def _compile_messages(self) -> List[Dict[str, str]]:
        """Safely assembles the system instruction context together with active sliding history."""
        return [self.system_instruction] + self.history

    def send_message(self, user_input: str) -> str:
        """
        Sends a sanitized input payload to the model pipeline with complete fault isolation.
        """
        clean_input = self._sanitize_input(user_input)
        if not clean_input:
            return "System Warning: Input payload was empty or invalid."

        # 1. Register sanitized user payload to active chat history state
        self.history.append({"role": "user", "content": clean_input})
        
        # 2. Re-balance sliding context boundaries defensively
        self._enforce_history_sliding_window()

        logger.info(f"Dispatching visual chat completion matrix request to model: {self.model}")
        
        # 3. Request inference under strict isolated error handling walls
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._compile_messages(),
                timeout=30.0 # Prevent the application thread from hanging indefinitely
            )
            
            # Secure dictionary value lookup validation routines
            reply = response.choices[0].message.content
            if not reply:
                raise ValueError("Received an empty response payload from the API provider.")

            # 4. Save assistant execution metrics to preserve future context states
            self.history.append({"role": "assistant", "content": reply})
            return reply

        except OpenAIError as api_err:
            logger.error(f"OpenAI Network API Gateway failed securely: {api_err}")
            # Fault Isolation: Remove the last unanswered user prompt to keep history states synchronized
            if self.history and self.history[-1]["role"] == "user":
                self.history.pop()
            return "Error: Unable to process request due to an external network service disturbance."
            
        except Exception as system_err:
            logger.critical(f"Internal computation engine failure encountered: {system_err}")
            return "Error: An isolated internal engine anomaly took place."

# =====================================================================
# Main Execution Safety Context
# =====================================================================
if __name__ == "__main__":
    # Ensure environment variables are loaded (For local system testing environments)
    # os.environ["OPENAI_API_KEY"] = "sk-proj-..." 

    try:
        engine = AIConversationEngine(model="gpt-4o", max_history_turns=5)
        
        # Safe structural dialog loop tests
        print(engine.send_message("Hi, my name is Alex."))
        print(engine.send_message("What is my name again?"))
    except ValueError as config_err:
        print(f"[Initialization Failed Check]: {config_err}")
