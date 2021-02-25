from os import environ
environ["CORE_CONFIG_SEED"] = "file:config/pylon.yml"
environ["CORE_DEVELOPMENT_MODE"] = 'true'

from pylon import main

main.main()
