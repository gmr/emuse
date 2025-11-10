import pathlib

import jinja2

from emuse import common

STATIC_PATH = pathlib.Path(__file__).parent / 'static'
TEMPLATE_PATH = pathlib.Path(__file__).parent / 'templates'

_environment: jinja2.Environment | None = None


def initialize() -> None:
    global _environment
    settings = common.Settings()
    _environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        autoescape=True,
        auto_reload=settings.debug,
        extensions=['jinja2.ext.i18n', 'jinja2_time.TimeExtension'],
        undefined=jinja2.StrictUndefined,
        enable_async=True,
    )


def render(template: str, **kwargs) -> str:
    """Render a template

    Args:
        template: Name of the template file
        **kwargs: Variables to pass to the template during rendering

    """
    template = _environment.get_template(template)
    return template.render(**kwargs)


async def render_async(template: str, **kwargs) -> str:
    """Render a template asynchronously

    Args:
        template: Name of the template file
        **kwargs: Variables to pass to the template during rendering

    """
    template = _environment.get_template(template)
    return await template.render_async(**kwargs)
