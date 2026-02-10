"""Test script for page_spec parser."""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.page_generator.parser import load_page_spec


def test_minimal_spec():
    """Test loading minimal YAML spec."""
    yaml_path = Path(__file__).parent / "test_minimal.yaml"

    print(f"Loading {yaml_path}...")
    try:
        spec = load_page_spec(yaml_path)
        print("SUCCESS: YAML loaded and validated")
        print(f"\nDashboard ID: {spec.metadata.dashboard_id}")
        print(f"ID Prefix: {spec.metadata.id_prefix}")
        print(f"Dataset ID: {spec.metadata.dataset_id}")
        print(f"Title: {spec.metadata.title}")
        print(f"\nColumn Map: {spec.column_map}")
        print(f"\nFilters: {len(spec.filters)}")
        for f in spec.filters:
            print(f"  - {f.id} ({f.type}): {f.label}")
        print(f"\nComponents: {len(spec.components)}")
        for c in spec.components:
            print(f"  - {c.id} ({c.type}): {c.title}")
        print(f"\nLayout sections: {len(spec.layout.sections)}")
        for idx, section in enumerate(spec.layout.sections):
            print(f"  Section {idx}: {len(section.rows)} rows")
            for row_idx, row in enumerate(section.rows):
                print(f"    Row {row_idx}: {len(row.items)} items")
                for item in row.items:
                    print(f"      - {item.component_id} (md={item.md})")

        print("\nAll validations passed!")
        return True
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = test_minimal_spec()
    exit(0 if success else 1)
