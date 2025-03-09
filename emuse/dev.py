"""This module is for running fastapi dev server only as:

fastapi dev emuse/dev.py

"""
from emuse import common, config
from emuse.main import create_app

app = create_app()
common.configure_logfire(app)
common.configure_logging(config.env_vars.get('debug', False) == '1')
