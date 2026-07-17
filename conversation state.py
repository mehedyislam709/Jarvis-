import openai

class AIConversationEngine:
    def __init__(self, model="gpt-4o"):
        self.client = openai.OpenAI(api_key="YOUR_API_KEY")
        self.model = model
        # The history list maintains the state of the conversation
        self.history = [
            {"role": "system", "content": "You are a helpful, witty coding assistant."}
        ]

    def send_message(self, user_input: str) -> str:
        # 1. Append the user's new message to the history
        self.history.append({"role": "user", "content": user_input})
        
        # 2. Request the next response from the model
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        
        # 3. Extract the assistant's reply
        reply = response.choices[0].message.content
        
        # 4. Append the assistant's response to keep the context for next time
        self.history.append({"role": "assistant", "content": reply})
        
        return reply

# --- Usage Example ---
engine = AIConversationEngine()
print(engine.send_message("Hi, my name is Alex."))
print(engine.send_message("What is my name again?")) # The engine remembers!
