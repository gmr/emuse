"""This module is for running fastapi dev server only as:

fastapi dev emuse/dev.py

"""

from emuse import common, main

app = main.create_app()
settings = common.Settings()
common.configure_logging(settings.debug)
