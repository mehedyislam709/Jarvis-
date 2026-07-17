class Settings:
    def __init__(self):
        self.name = "Jarvis"          # System name
        self.version = "1.0.0"         # Project version
        self.language = "en"           # Language (e.g., en, bn)
        self.rate = 175                # Voice speed (TTS Rate)
        self.volume = 1.0              # Sound volume (0.0 to 1.0)
        self.model = "gemini-pro"      # LLM model name

settings = Settings()
