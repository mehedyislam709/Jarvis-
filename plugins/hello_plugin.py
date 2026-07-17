from core.plugin_manager import BasePlugin


class Plugin(BasePlugin):
    name = "HelloPlugin"
    version = "1.0"

    def activate(self):
        print("HelloPlugin activated")

    def deactivate(self):
        print("HelloPlugin deactivated")

    def execute(self, user_name="User"):
        return f"Hello, {user_name}! I am Jarvis."
