"""Test validation rules for PageSpec."""
import sys
from pathlib import Path
import tempfile
import yaml

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.page_generator.parser import load_page_spec
from pydantic import ValidationError


def test_duplicate_ids():
    """Test that duplicate IDs are detected."""
    spec_data = {
        "metadata": {
            "dashboard_id": "test",
            "id_prefix": "test-",
            "dataset_id": "test-ds",
            "title": "Test",
        },
        "column_map": {"col1": "column_1"},
        "filters": [
            {"type": "category", "id": "test-filter-1", "label": "Filter 1", "column": "col1"},
        ],
        "layout": {
            "sections": [
                {
                    "rows": [
                        {"items": [{"component_id": "test-filter-1", "md": 12}]}
                    ]
                }
            ]
        },
        "components": [
            {
                "type": "kpi",
                "id": "test-filter-1",  # Duplicate ID!
                "title": "KPI",
                "spec": {"value_column": "col1", "agg_func": "sum"},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(spec_data, f)
        temp_path = Path(f.name)

    try:
        load_page_spec(temp_path)
        print("FAIL: Should have detected duplicate IDs")
        return False
    except ValidationError as e:
        if "Duplicate IDs found" in str(e):
            print("PASS: Duplicate ID detection works")
            return True
        else:
            print(f"FAIL: Wrong error: {e}")
            return False
    finally:
        temp_path.unlink()


def test_unknown_column():
    """Test that unknown column references are detected."""
    spec_data = {
        "metadata": {
            "dashboard_id": "test",
            "id_prefix": "test-",
            "dataset_id": "test-ds",
            "title": "Test",
        },
        "column_map": {"col1": "column_1"},
        "filters": [
            {"type": "category", "id": "test-filter-1", "label": "Filter 1", "column": "col1"},
        ],
        "layout": {
            "sections": [
                {
                    "rows": [
                        {"items": [{"component_id": "test-chart-1", "md": 12}]}
                    ]
                }
            ]
        },
        "components": [
            {
                "type": "chart",
                "id": "test-chart-1",
                "title": "Chart",
                "spec": {
                    "title": "Chart",
                    "chart_type": "bar",
                    "x_column": "unknown_col",  # Unknown column!
                    "y_columns": ["col1"],
                },
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(spec_data, f)
        temp_path = Path(f.name)

    try:
        load_page_spec(temp_path)
        print("FAIL: Should have detected unknown column")
        return False
    except ValidationError as e:
        if "unknown x_column" in str(e).lower():
            print("PASS: Unknown column detection works")
            return True
        else:
            print(f"FAIL: Wrong error: {e}")
            return False
    finally:
        temp_path.unlink()


def test_invalid_layout_reference():
    """Test that invalid layout references are detected."""
    spec_data = {
        "metadata": {
            "dashboard_id": "test",
            "id_prefix": "test-",
            "dataset_id": "test-ds",
            "title": "Test",
        },
        "column_map": {"col1": "column_1"},
        "filters": [],
        "layout": {
            "sections": [
                {
                    "rows": [
                        {"items": [{"component_id": "non-existent-component", "md": 12}]}
                    ]
                }
            ]
        },
        "components": [
            {
                "type": "kpi",
                "id": "test-kpi-1",
                "title": "KPI",
                "spec": {"value_column": "col1", "agg_func": "sum"},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(spec_data, f)
        temp_path = Path(f.name)

    try:
        load_page_spec(temp_path)
        print("FAIL: Should have detected invalid layout reference")
        return False
    except ValidationError as e:
        if "unknown component_id" in str(e).lower():
            print("PASS: Invalid layout reference detection works")
            return True
        else:
            print(f"FAIL: Wrong error: {e}")
            return False
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    print("Running validation tests...\n")

    results = []
    results.append(("Duplicate IDs", test_duplicate_ids()))
    results.append(("Unknown Column", test_unknown_column()))
    results.append(("Invalid Layout Reference", test_invalid_layout_reference()))

    print("\n" + "=" * 50)
    print("Test Results:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")

    all_passed = all(r[1] for r in results)
    print("=" * 50)
    if all_passed:
        print("\nAll validation tests passed!")
    else:
        print("\nSome validation tests failed!")

    exit(0 if all_passed else 1)
