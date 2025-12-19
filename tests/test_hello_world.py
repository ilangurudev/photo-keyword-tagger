"""Tests for the hello_world module."""

import pytest
from photo_keyword_tagger.hello_world import say_hello


def test_say_hello_default():
    """Test say_hello with default parameter."""
    result = say_hello()
    assert result == "Hello, World! Welcome to Photo Keyword Tagger."


def test_say_hello_custom_name():
    """Test say_hello with custom name."""
    result = say_hello("Alice")
    assert result == "Hello, Alice! Welcome to Photo Keyword Tagger."


def test_say_hello_empty_string():
    """Test say_hello with empty string."""
    result = say_hello("")
    assert result == "Hello, ! Welcome to Photo Keyword Tagger."

