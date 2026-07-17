default_voice = config.get("voice.default")

voice_profile = config.get(
    f"voice.profiles.{default_voice}"
)
