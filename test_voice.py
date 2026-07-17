default_voice = config.get("voice.default")

voice_profile = config.get(
    f"voice.profiles.{default_voice}"
)
config.set("voice.default", "male")
config.save()
config.set("voice.default", "female")
config.save()
