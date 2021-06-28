from os import environ
environ["CORE_CONFIG_SEED"] = "file:config/pylon.yml"
environ["CORE_DEVELOPMENT_MODE"] = 'true'
# environ["APP_HOST"] = "http://192.168.1.215"

from pylon import main

main.main()
