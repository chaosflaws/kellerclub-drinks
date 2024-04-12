from typing import Any

from jinja2 import TemplateError, Environment


def render_template(env: Environment, path: str, url: str,
                    **values: Any):
    template = None
    try:
        template = env.get_template(path)
        return template.render(url=url, **values)
    except TemplateError as e:
        print(f'Template {template.filename if template else "<Pre-Template>"}')
        raise TemplateError(e.message) from e
