import pathlib

import pydantic_settings

BASE_DIR = pathlib.Path(__file__).parent.parent

_env_settings = pydantic_settings.EnvSettingsSource(
    settings_cls=pydantic_settings.BaseSettings)
_dot_env_settings = pydantic_settings.DotEnvSettingsSource(
    settings_cls=pydantic_settings.BaseSettings, env_file=BASE_DIR / '.env')
_env_settings.env_vars.update(_dot_env_settings.env_vars)

env_vars = _env_settings.env_vars
