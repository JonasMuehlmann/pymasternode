#!/bin/python
import pytest

from src import wallet


def test_generate_label_iter_shorter():
    generated_label: str = wallet.generate_label("COINW001MN###", 10)
    assert generated_label == "COINW001MN010"


def test_generate_label_iter_equal():
    generated_label: str = wallet.generate_label("COINW001MN##", 10)
    assert generated_label == "COINW001MN10"


def test_generate_label_iter_longer():
    with pytest.raises(IndexError):
        generated_label: str = wallet.generate_label("COINW001MN##", 100)
