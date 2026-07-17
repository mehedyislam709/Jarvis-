import logging

# Setting up a basic logger for the engine
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ConversationEngine:
    def __init__(self, stt, brain, tts):
        """
        Initializes the Core Conversation Engine.
        :param stt: Speech-to-Text module (handles audio input)
        :param brain: LLM/AI module (handles text generation/processing)
        :param tts: Text-to-Speech module (handles audio output response)
        """
        self.stt = stt
        self.brain = brain
        self.tts = tts
        self._is_running = False

    def start(self):
        """Starts the main conversation loop."""
        self._is_running = True
        logging.info("Jarvis Conversation Engine activated.")

        try:
            while self._is_running:
                print("\nListening for command...")
                
                # 1. Capture Audio & Convert to Text
                user_input = self.stt.listen() 
                if not user_input or user_input.strip() == "":
                    continue

                logging.info(f"User said: {user_input}")

                # 2. Check for an explicit exit command
                if any(word in user_input.lower() for word in ["exit", "stop", "goodbye"]):
                    self.stop()
                    break

                # 3. Process the input through the AI Brain
                try:
                    ai_response = self.brain.process(user_input)
                    logging.info(f"Jarvis response: {ai_response}")
                except Exception as brain_error:
                    logging.error(f"Brain processing failed: {brain_error}")
                    ai_response = "I encountered an error trying to process that."

                # 4. Speak the response out loud
                if ai_response:
                    self.tts.speak(ai_response)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logging.critical(f"Critical failure in Conversation Engine: {e}")
            self.stop()

    def stop(self):
        """Safely stops the conversation loop."""
        if self._is_running:
            self._is_running = False
            logging.info("Stopping Conversation Engine...")
            self.tts.speak("Goodbye!")

