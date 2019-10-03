"""Interact with the wallet."""
import getpass
import json
import re
import subprocess
from pathlib import PosixPath
from subprocess import CompletedProcess
from typing import Dict, List, Match, Optional, Union

from src import pymasternode
from src.helpers import Genkey, Label, Path, ReceivingAddress


MODULE_SETTINGS: Dict[str, Union[str, int, Path]] = {
    "PATH_MN_CONF"   : Path(""),
    "PATH_WALLET_CLI": Path(""),
    "NODE_TERM"      : "",
    "NODE_PORT"      : -1,
}


def set_coin(name: str) -> None:
    """Set MODULE_SETTINGS["PATH_MN_CONF"] and MODULE_SETTINGS["PATH_WALLET_CLI"] to the paths of the chosen coin.

    Args:
        name: The name of the coin to be used

    """
    # noinspection PyTypeChecker
    MODULE_SETTINGS["PATH_MN_CONF"] = PosixPath(
        pymasternode.CONFIG["coins"][name]["mn_conf_path"]
    ).expanduser()
    # noinspection PyTypeChecker
    MODULE_SETTINGS["PATH_WALLET_CLI"] = PosixPath(
        pymasternode.CONFIG["coins"][name]["wallet_cli_path"]
    ).expanduser()
    # noinspection PyTypeChecker
    MODULE_SETTINGS["NODE_PORT"] = int(pymasternode.CONFIG["coins"][name]["node_port"])
    if name == "SMART":
        MODULE_SETTINGS["NODE_TERM"] = "smartnode"
    else:
        MODULE_SETTINGS["NODE_TERM"] = "masternode"


def generate_label(addr_scheme: str, iterator: int) -> Label:
    """
    Generate a label.

    Args:
        addr_scheme: the naming scheme of the label, insert a ### for the iterator placeholder (example:
        Coin-W001-MN###)
        iterator: The iterator that gets put into the placeholder

    Returns:
        The generated address
    """
    return Label(
        (
            addr_scheme.split("###", 2)[0]
            + str(iterator).zfill(addr_scheme.count("#"))
            + addr_scheme.split("###", 2)[1]
        )
    )


def generate_address(label: Label) -> ReceivingAddress:
    """
    Generate a receiving address.

    Args:
        label: The label of the generated receiving address

    Returns:
        The generated receiving address
    """
    return ReceivingAddress(
        subprocess.run(
            [
                MODULE_SETTINGS["PATH_WALLET_CLI"],
                "-server",
                "getnewaddress",
                str(label),
            ],
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).stdout
    )


def generate_genkey() -> Genkey:
    """
    Generate a masternode genkey.

    Returns:
        The generated masternode genkey

    """
    return Genkey(
        subprocess.run(
            [
                MODULE_SETTINGS["PATH_WALLET_CLI"],
                "-server",
                MODULE_SETTINGS["NODE_TERM"],
                "genkey",
            ],
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).stdout
    )


def generate_config_lines(
    addr_scheme: str, iterator_start: int, iterator_end: int, append: bool = False
) -> None:
    """
    Generate config lines consisting of the following items; label, port, genkey and address.

    Args:
        addr_scheme: The naming scheme of the labels, insert ### to indicate the label iterator
        iterator_start: The start of the label iterator
        iterator_end: The inclusive end of the label iterator
        append: Lines will be appended to the existing config if True, written into data/conf_lines otherwise

    """
    iterator: int = int(iterator_start)
    lines: List[str] = []

    for _ in range(iterator_start, iterator_end + 1):
        label: Label = generate_label(addr_scheme, iterator)

        line: str = (
            label
            + f" :{str(MODULE_SETTINGS['NODE_PORT'])} "
            + generate_genkey().__str__()
            + " Address:"
            + generate_address(label).__str__()
            + "\n"
        )
        print(line, "\n")
        lines.append(line)
        iterator += 1

    if append:
        with open(MODULE_SETTINGS["PATH_MN_CONF"], "a") as config:
            config.writelines(lines)
        print("Line(s) appended to existing config file.")
    else:
        with open(
            pymasternode.PATH_PROJECT_ROOT / "data" / "conf_lines.txt", "w"
        ) as output:
            output.writelines(lines)
        print("Saving output to data/conf_lines.txt.\n")


def get_mn_outputs() -> None:
    """
    Generate mn outputs and append correct TX_ID to lines in masternode.conf."""
    mn_outputs_json: CompletedProcess = subprocess.run(
        [MODULE_SETTINGS["PATH_WALLET_CLI"], "-server", "masternode", "outputs"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    mn_outputs_dict = json.loads(mn_outputs_json.stdout.strip())
    with open(MODULE_SETTINGS["PATH_MN_CONF"], "r") as conf:
        config_lines: List[str] = conf.readlines()

    with open(MODULE_SETTINGS["PATH_MN_CONF"], "r") as conf:
        for line_i, line in enumerate(conf):
            # Line ending in 0 or 1 (Tx-ID)
            if not re.search(r"\W\b[01]$", line):
                # Line ending in a mixed-char-string of length 64 (TX_hash)
                match: Optional[Match[str]] = re.search(r"\b\w{64}$", line)
                for key in mn_outputs_dict:
                    if match and mn_outputs_dict[key].get("txhash") == match.group(0):
                        config_lines[line_i] = (
                            line.rstrip()
                            + " "
                            + mn_outputs_dict[key].get("txoutput")
                            + "\n"
                        )
    # Writes updated lines to file
    with open(MODULE_SETTINGS["PATH_MN_CONF"], "w") as config:
        config.writelines(config_lines)


def unlock_wallet(timeout: int = 60, max_attempts: int = 3) -> None:
    """
    Unlock the wallet with your passphrase for a specified time.

    internal helper function will be called max_attempts times until the unlock is successful.

    Args:
        timeout: time in seconds to unlock the wallet for
        max_attempts: maximum attempts before aborting
    """

    def unlock(timeout: int) -> bool:
        """Returns:
            True if unlock was successful, False otherwise
        """
        try:
            subprocess.run(
                [
                    MODULE_SETTINGS["PATH_WALLET_CLI"],
                    "walletpassphrase",
                    getpass.getpass("Enter passphrase: "),
                    str(timeout),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                check=True,
            )
            print("Wallet unlocked")
            return True

        except subprocess.CalledProcessError:
            print("Unlock failed, try again")
            return False

    # attempts: int = max_attempts
    # while True:
    #     if attempts == 0:
    #         print("Reached max attempts, aborting!")
    #         break
    #     else:
    #         attempts -= 1
    #         if unlock(timeout):
    #             break

    for i in range(1, max_attempts + 1):
        if unlock(timeout):
            break
        else:
            print(f"{max_attempts - i} attempt(s) left")
    else:
        print("Reached max attempts, aborting!")


def start_mn(masternodes: List[Label] = None) -> None:
    """
    Start masternodes.

    Args:
        masternodes: Labels of masternodes to be started, if not provided: all missing MN's will be started

    """
    if masternodes:
        for masternode in masternodes:
            subprocess.run(
                [
                    MODULE_SETTINGS["PATH_WALLET_CLI"],
                    "-server",
                    MODULE_SETTINGS["NODE_TERM"],
                    "start-alias",
                    masternode,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                check=True,
            )
    else:
        subprocess.run(
            [
                MODULE_SETTINGS["PATH_WALLET_CLI"],
                "-server",
                MODULE_SETTINGS["NODE_TERM"],
                "start-missing",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=True,
        )
    print("Masternodes started.")


def main() -> None:
    set_coin("GLT")


main()
