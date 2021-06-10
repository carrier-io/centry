from os import environ
environ["APP_HOST"] = "http://127.0.0.1"


environ["CORE_DEVELOPMENT_MODE"] = 'true'
environ["CORE_DEBUG_LOGGING"] = 'true'
environ["CORE_CONFIG_SEED"] = 'file:config/pylon.yml'

from pylon import main

main.main()
