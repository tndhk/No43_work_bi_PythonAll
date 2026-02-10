"""Generator for _filters.py file."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ..schema import PageSpec


def generate_filters(spec: PageSpec) -> str:
    """Generate _filters.py from PageSpec.

    Args:
        spec: Validated PageSpec object

    Returns:
        Generated Python code as string
    """
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        extensions=['jinja2.ext.do']
    )
    template = env.get_template("filters.py.j2")

    return template.render(spec=spec)
