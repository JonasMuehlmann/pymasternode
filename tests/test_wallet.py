#!/bin/python
from src import wallet


def test_generate_label():
    generated_label: str = wallet.generate_label("COINW001MN###", 10)
    assert generated_label == "COINW001MN010"

    generated_label: str = wallet.generate_label("COINW001MN##", 10)
    assert generated_label == "COINW001MN10"
