# Inside your CompanyPlatform class
def run_business_logic(self, task: str):
    # Announce the task
    self.tts = TextToSpeechManager(offline_mode=True)
    self.tts.speak(f"Manager David has received a new directive: {task}")
    
    # Continue your normal execution flow...
    report = self.manager.delegate_and_execute(task)
