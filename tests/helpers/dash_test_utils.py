"""Shared Dash component tree test utilities.

These helper functions provide recursive search and extraction capabilities
for Dash component trees, eliminating duplication across test files.
"""
from __future__ import annotations

from typing import Any, Optional


def find_component_by_id(
    component: Any, target_id: str
) -> Optional[Any]:
    """Recursively search a Dash component tree for a component with the given id.

    Args:
        component: The root Dash component to search from.
        target_id: The id string to match against component.id.

    Returns:
        The first matching component, or None if not found.
    """
    # Check current component
    if hasattr(component, "id") and component.id == target_id:
        return component

    # Search children
    children = getattr(component, "children", None)
    if children is None:
        return None

    if isinstance(children, (list, tuple)):
        for child in children:
            result = find_component_by_id(child, target_id)
            if result is not None:
                return result
    elif isinstance(children, str):
        # String children cannot have an id -- skip
        return None
    else:
        return find_component_by_id(children, target_id)

    return None


def find_components_by_type(
    component: Any, target_type: type
) -> list[Any]:
    """Recursively find all components of a given type in a Dash component tree.

    Args:
        component: The root Dash component to search from.
        target_type: The type (class) to match against, e.g. html.H1.

    Returns:
        A list of all matching components (empty list if none found).
    """
    results: list[Any] = []

    if isinstance(component, target_type):
        results.append(component)

    children = getattr(component, "children", None)
    if children is None:
        return results

    if isinstance(children, (list, tuple)):
        for child in children:
            results.extend(find_components_by_type(child, target_type))
    elif isinstance(children, str):
        # String children are not components -- skip
        pass
    else:
        results.extend(find_components_by_type(children, target_type))

    return results


def extract_text_recursive(component: Any) -> str:
    """Extract all text content from a Dash component tree.

    Walks the tree depth-first and concatenates all string children
    separated by spaces.

    Args:
        component: The root Dash component to extract text from.

    Returns:
        A single string containing all text content, space-separated.
    """
    texts: list[str] = []
    children = getattr(component, "children", None)

    if isinstance(children, str):
        texts.append(children)
    elif isinstance(children, (list, tuple)):
        for child in children:
            if isinstance(child, str):
                texts.append(child)
            elif hasattr(child, "children"):
                texts.append(extract_text_recursive(child))
    elif hasattr(children, "children"):
        texts.append(extract_text_recursive(children))

    return " ".join(texts)


def extract_dropdown_options(
    component: Any, dropdown_id: str
) -> Optional[list[dict]]:
    """Find a dropdown by id in the component tree and return its options.

    Args:
        component: The root Dash component to search from.
        dropdown_id: The id of the dropdown to find.

    Returns:
        The options list of the dropdown, or None if not found.
    """
    def _walk(comp: Any) -> Optional[list[dict]]:
        # Check if this component matches the dropdown id
        if hasattr(comp, "id") and comp.id == dropdown_id:
            return getattr(comp, "options", None)

        # Recurse into children
        children = getattr(comp, "children", None)
        if children is None:
            return None
        if not isinstance(children, (list, tuple)):
            children = [children]
        for child in children:
            if child is None:
                continue
            result = _walk(child)
            if result is not None:
                return result
        return None

    return _walk(component)


def extract_dropdown_value(
    component: Any, dropdown_id: str
) -> Any:
    """Find a dropdown by id in the component tree and return its current value.

    Args:
        component: The root Dash component to search from.
        dropdown_id: The id of the dropdown to find.

    Returns:
        The value of the dropdown, or None if not found.
    """
    def _walk(comp: Any) -> Any:
        if hasattr(comp, "id") and comp.id == dropdown_id:
            return getattr(comp, "value", None)

        children = getattr(comp, "children", None)
        if children is None:
            return None
        if not isinstance(children, (list, tuple)):
            children = [children]
        for child in children:
            if child is None:
                continue
            result = _walk(child)
            if result is not None:
                return result
        return None

    return _walk(component)
