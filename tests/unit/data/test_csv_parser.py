"""Tests for CSV parser."""
import pytest
import pandas as pd
from src.data.csv_parser import (
    detect_encoding,
    parse_preview,
    parse_full,
    CsvImportOptions,
)


def test_detect_encoding_utf8():
    """Test: Encoding detection for UTF-8."""
    # Given: UTF-8 encoded bytes
    text = "name,value\nAlice,100"
    file_bytes = text.encode("utf-8")

    # When: Detecting encoding
    encoding = detect_encoding(file_bytes)

    # Then: UTF-8 is detected (or compatible encoding)
    assert encoding in ["utf-8", "ascii"]


def test_parse_preview():
    """Test: parse_preview reads limited rows."""
    # Given: CSV with many rows
    csv_content = "id,name\n" + "\n".join([f"{i},Name{i}" for i in range(2000)])
    file_bytes = csv_content.encode("utf-8")

    # When: Parsing preview
    df = parse_preview(file_bytes, max_rows=100)

    # Then: Limited rows are read
    assert len(df) <= 100


def test_parse_full():
    """Test: parse_full reads all rows."""
    # Given: CSV with many rows
    csv_content = "id,name\n" + "\n".join([f"{i},Name{i}" for i in range(100)])
    file_bytes = csv_content.encode("utf-8")

    # When: Parsing full
    df = parse_full(file_bytes)

    # Then: All rows are read
    assert len(df) == 100


def test_parse_with_custom_options():
    """Test: CSV parsing with custom options."""
    # Given: CSV with custom delimiter
    csv_content = "id|name\n1|Alice\n2|Bob"
    file_bytes = csv_content.encode("utf-8")
    options = CsvImportOptions(delimiter="|")

    # When: Parsing with options
    df = parse_full(file_bytes, options=options)

    # Then: Correctly parsed
    assert len(df) == 2
    assert "id" in df.columns
    assert "name" in df.columns


def test_parse_empty_file():
    """Test: Parsing empty CSV file."""
    # Given: Empty CSV
    file_bytes = b""

    # When: Parsing
    df = parse_full(file_bytes)

    # Then: Empty DataFrame is returned
    assert len(df) == 0
