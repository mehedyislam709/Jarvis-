class VoiceManager:

    def __init__(self, config):
        self.config = config

    def current_profile(self):
        name = self.config.get("voice.default")
        return self.config.get(f"voice.profiles.{name}")

    def switch(self, profile_name):
        if self.config.has(f"voice.profiles.{profile_name}"):
            self.config.set("voice.default", profile_name)
            self.config.save()
