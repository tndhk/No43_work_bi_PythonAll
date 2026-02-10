#!/usr/bin/env python3
"""Fix page_spec.yaml layout structure to match schema."""
import yaml
from pathlib import Path

def fix_layout_section(section):
    """Fix a single layout section to match schema."""
    # If section has 'items' directly, it's already correct (for filter rows)
    if 'items' in section:
        return section

    # If section has 'rows', need to transform rows -> columns -> items
    # to rows -> items
    if 'rows' in section:
        new_rows = []
        for row in section['rows']:
            if 'columns' in row:
                # Extract items from columns
                items = []
                for col in row['columns']:
                    md = col.get('md', 12)
                    className = col.get('className')
                    col_items = col.get('items', [])

                    for item in col_items:
                        # Add md and className to each item
                        new_item = dict(item)
                        new_item['md'] = md
                        if className:
                            new_item['className'] = className
                        items.append(new_item)

                new_row = {'items': items}
                if 'className' in row:
                    new_row['className'] = row['className']
                new_rows.append(new_row)
            elif 'items' in row:
                # Already correct format
                new_rows.append(row)

        section['rows'] = new_rows

    return section


def fix_kpi_component(component):
    """Add spec field to KPI components."""
    if component.get('type') != 'kpi':
        return component

    # If spec already exists, return as-is
    if 'spec' in component:
        return component

    # Create spec from top-level fields
    spec = {}

    # Extract value_column from data_transform if present
    if 'data_transform' in component:
        dt = component['data_transform']
        if isinstance(dt, dict) and 'operations' in dt:
            # Look for count_rows operation
            for op in dt['operations']:
                if op.get('type') == 'count_rows':
                    spec['value_column'] = None  # Will be computed
                    spec['agg_func'] = 'count'
                    break

    # Add colors if present at top level
    if 'bg_color' in component:
        spec['color_bg'] = component['bg_color']
    if 'accent_color' in component:
        spec['color_accent'] = component['accent_color']

    component['spec'] = spec
    return component


def main():
    yaml_path = Path('src/pages/hamm_overview/page_spec.yaml')

    # Load YAML
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    # Fix layout sections
    if 'layout' in data and 'sections' in data['layout']:
        data['layout']['sections'] = [
            fix_layout_section(section)
            for section in data['layout']['sections']
        ]

    # Fix KPI components
    if 'components' in data:
        data['components'] = [
            fix_kpi_component(component)
            for component in data['components']
        ]

    # Write back
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    print(f"Fixed {yaml_path}")
    print("Layout sections:", len(data['layout']['sections']))
    print("Components:", len(data['components']))


if __name__ == '__main__':
    main()
