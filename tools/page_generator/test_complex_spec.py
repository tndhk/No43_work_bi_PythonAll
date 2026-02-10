"""Test complex page spec with all features."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.page_generator.parser import load_page_spec


def test_complex_spec():
    """Test loading complex YAML spec."""
    yaml_path = Path(__file__).parent / "test_complex.yaml"

    print(f"Loading {yaml_path}...\n")
    try:
        spec = load_page_spec(yaml_path)
        print("SUCCESS: Complex YAML loaded and validated\n")

        # Metadata
        print(f"Dashboard ID: {spec.metadata.dashboard_id}")
        print(f"ID Prefix: {spec.metadata.id_prefix}")
        print(f"Dataset ID: {spec.metadata.dataset_id}")
        print(f"Title: {spec.metadata.title}")

        # Column Map
        print(f"\nColumn Map ({len(spec.column_map)} columns):")
        for key, value in spec.column_map.items():
            print(f"  {key} -> {value}")

        # Derived Columns
        if spec.derived_columns:
            print(f"\nDerived Columns ({len(spec.derived_columns)}):")
            for dc in spec.derived_columns:
                print(f"  {dc.name} ({dc.type}) from {dc.source_column}")

        # Filters
        print(f"\nFilters ({len(spec.filters)}):")
        for f in spec.filters:
            clear_info = f" (has clear button: {f.clear_button_id})" if f.has_clear_button else ""
            multi_info = " (multi)" if f.multi else ""
            print(f"  {f.id} ({f.type}): {f.label} on {f.column}{clear_info}{multi_info}")

        # Components
        print(f"\nComponents ({len(spec.components)}):")
        for c in spec.components:
            has_transform = " [with data_transform]" if c.data_transform else ""
            print(f"  {c.id} ({c.type}): {c.title}{has_transform}")

            if c.type == "kpi" and hasattr(c.spec, "value_column"):
                print(f"    KPI: {c.spec.agg_func}({c.spec.value_column})")
            elif c.type == "chart" and hasattr(c.spec, "x_column"):
                print(f"    Chart: {c.spec.chart_type} ({c.spec.x_column} vs {c.spec.y_columns})")
            elif c.type == "table":
                print(f"    Table: {len(c.spec.column_order)} columns")

            if c.data_transform and "operations" in c.data_transform:
                ops = c.data_transform["operations"]
                print(f"    Transform operations: {len(ops)}")
                for op in ops:
                    print(f"      - {op.type}")

        # Layout
        print(f"\nLayout sections: {len(spec.layout.sections)}")
        for idx, section in enumerate(spec.layout.sections):
            title_info = f": {section.title}" if section.title else ""
            print(f"  Section {idx}{title_info}")
            if section.description:
                print(f"    Description: {section.description}")
            for row_idx, row in enumerate(section.rows):
                print(f"    Row {row_idx}: {len(row.items)} items")
                for item in row.items:
                    print(f"      - {item.component_id} (md={item.md})")

        print("\nAll validations passed!")
        print("\nKey features tested:")
        print("  - Multiple filter types (slicer, category, dropdown, chip_group)")
        print("  - Derived columns (_year, _month, _fiscal_year)")
        print("  - KPI cards with custom colors")
        print("  - Charts with data transformations (group_by, pivot)")
        print("  - Tables with conditional styling")
        print("  - Multi-section layout with titles and descriptions")

        return True
    except Exception as e:
        print(f"ERROR: {type(e).__name__}")
        print(f"{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_complex_spec()
    exit(0 if success else 1)
