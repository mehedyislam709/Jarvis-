import whisper

class SpeechToText:
    def __init__(self, model_size="large-v3"):
        print("Loading Whisper model for maximum accuracy...")
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path):
        print(f"Transcribing audio from: {audio_path}")
        result = self.model.transcribe(audio_path)
        return result["text"]
