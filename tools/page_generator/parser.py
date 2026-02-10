"""YAML parser for page_spec.yaml."""
from pathlib import Path
import yaml
from pydantic import ValidationError

from .schema import PageSpec


def load_page_spec(yaml_path: Path) -> PageSpec:
    """Load and validate page_spec.yaml into PageSpec object.

    Args:
        yaml_path: Path to page_spec.yaml

    Returns:
        Validated PageSpec object

    Raises:
        FileNotFoundError: If yaml_path does not exist
        ValidationError: If YAML structure is invalid
        yaml.YAMLError: If YAML syntax is invalid
    """
    if not yaml_path.exists():
        raise FileNotFoundError(f"page_spec.yaml not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Pydantic validation
    try:
        spec = PageSpec(**data)
    except ValidationError as e:
        # Re-raise with more context
        raise ValidationError.from_exception_data(
            title=f"Validation failed for {yaml_path}",
            line_errors=e.errors(),
        ) from e

    return spec
