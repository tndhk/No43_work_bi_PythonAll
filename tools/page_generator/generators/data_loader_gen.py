"""Generator for _data_loader.py and _custom_logic.py files."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ..schema import PageSpec


def generate_data_loader(spec: PageSpec) -> str:
    """Generate _data_loader.py from PageSpec.

    Args:
        spec: Validated PageSpec object

    Returns:
        Generated Python code as string
    """
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        extensions=['jinja2.ext.do'],
    )

    # Add custom filters
    env.filters['replace'] = str.replace
    env.filters['upper'] = str.upper

    template = env.get_template("data_loader.py.j2")

    return template.render(spec=spec)


def generate_custom_logic(spec: PageSpec) -> str:
    """Generate _custom_logic.py skeleton from PageSpec.

    Args:
        spec: Validated PageSpec object

    Returns:
        Generated Python code as string
    """
    template_dir = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        extensions=['jinja2.ext.do'],
    )

    template = env.get_template("custom_logic.py.j2")

    return template.render(spec=spec)
