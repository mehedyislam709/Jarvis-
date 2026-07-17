from core.assistant import Jarvis
from core.logger import logger
​def main():
logger.info("Jarvis starting...")
jarvis = Jarvis()
jarvis.start()
​if name == "main":
main()
