import pathlib

import jinja2

from emuse import config

TEMPLATE_PATH = pathlib.Path(__file__).parent / 'templates'

_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
    autoescape=True,
    auto_reload=config.env_vars.get('debug', False) == '1',
    undefined=jinja2.StrictUndefined)


def render(template: str, **kwargs) -> str:
    """Render a template

    Args:
        template: Name of the template file
        **kwargs: Variables to pass to the template during rendering

    """
    template = _environment.get_template(template)
    return template.render(**kwargs)
