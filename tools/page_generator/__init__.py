"""Page generator package for declarative dashboard page creation."""
from .schema import (
    PageSpec,
    MetadataSpec,
    FilterSpec,
    ComponentSpec,
    LayoutSpec,
    ChartSpecYAML,
    TableSpecYAML,
    KPICardSpec,
    DerivedColumnSpec,
    DataTransformOperationSpec,
)
from .parser import load_page_spec
from .cli import main as cli_main

__all__ = [
    "PageSpec",
    "MetadataSpec",
    "FilterSpec",
    "ComponentSpec",
    "LayoutSpec",
    "ChartSpecYAML",
    "TableSpecYAML",
    "KPICardSpec",
    "DerivedColumnSpec",
    "DataTransformOperationSpec",
    "load_page_spec",
    "cli_main",
]
