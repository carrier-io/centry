from os import environ

from dotenv import load_dotenv
from pylon import main

load_dotenv()

environ["APP_HOST"] = "http://127.0.0.1"

environ["CORE_DEVELOPMENT_MODE"] = 'true'
environ["CORE_DEBUG_LOGGING"] = 'true'
environ["CORE_CONFIG_SEED"] = 'file:config/pylon.yml'

main.main()
