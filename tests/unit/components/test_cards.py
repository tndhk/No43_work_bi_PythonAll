"""Tests for KPI card components."""
import pytest
import dash_bootstrap_components as dbc
from src.components.cards import create_kpi_card


def test_create_kpi_card_with_int_value():
    """Test: KPI card with integer value."""
    # Given: Title and integer value
    title = "Total Sales"
    value = 1000
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_float_value():
    """Test: KPI card with float value."""
    # Given: Title and float value
    title = "Average Price"
    value = 99.99
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_string_value():
    """Test: KPI card with string value."""
    # Given: Title and string value
    title = "Status"
    value = "Active"
    
    # When: Creating KPI card
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_with_subtitle():
    """Test: KPI card with subtitle."""
    # Given: Title, value, and subtitle
    title = "Total Sales"
    value = 1000
    subtitle = "+5% vs last month"
    
    # When: Creating KPI card with subtitle
    card = create_kpi_card(title, value, subtitle)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None


def test_create_kpi_card_without_subtitle():
    """Test: KPI card without subtitle."""
    # Given: Title and value only (no subtitle)
    title = "Total Sales"
    value = 1000
    
    # When: Creating KPI card without subtitle
    card = create_kpi_card(title, value)
    
    # Then: Card component is created
    assert isinstance(card, dbc.Card)
    assert card is not None
