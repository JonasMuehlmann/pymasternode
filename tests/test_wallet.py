#!/bin/python
import subprocess

from src import wallet

subprocess_args = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.PIPE,
    "encoding": "utf-8",
}


# FIX: Specific to globaltoken
def setup_module():
    """Setup any state specific to the execution of the module."""

    if subprocess.run(
            ["pgrep", "-c", "globaltokend"],
            **subprocess_args
    ).stdout == "0":
        subprocess.run(
            [wallet.MODULE_SETTINGS["PATH_WALLET_BIN"] / "globaltokend"],
            check=True,
            **subprocess_args
        )

    def test_generate_label_iter_shorter():
        generated_label: str = wallet.generate_label("COINW001MN###", 10)
        assert generated_label == "COINW001MN010"

    def test_generate_label_iter_equal():
        generated_label: str = wallet.generate_label("COINW001MN##", 10)
        assert generated_label == "COINW001MN10"

    def test_generate_label_iter_longer():
        generated_label: str = wallet.generate_label("COINW001MN##", 100)
        assert generated_label == "COINW001MN100"


# FIX: Specific to globaltoken
def teardown_module(module):
    """Teardown any state that was previously setup with a setup_module method."""

    subprocess.run(["pkill", "globaltokend"], **subprocess_args)
