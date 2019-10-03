#!/bin/python
import re
import time
from pathlib import PosixPath
from typing import Any, Callable, List, NewType, Pattern, Union


Path = PosixPath
Label = NewType("Label", str)
Hostname = NewType("Hostname", str)
Command = NewType("Command", str)
Identifier = NewType("Identifier", Union[Label, "Ip", "Subid"])


def call_until_returns_true(
    function_name: Callable[[Any], bool],
    function_parameters: List[Any] = None,
    call_interval_seconds: float = 10.0,
) -> None:
    while not function_name(*function_parameters):
        time.sleep(call_interval_seconds)


# TODO: Inherit classes from string.
class Ip:
    """
    A string wrapped to represent an IPv4 address.

    Raises ValueError if __init__ does not get passed a valid address.\n
    Implements __str__, __repr__ and __len__.
    """

    def __init__(self, ip: str):
        ipv4_pattern: Pattern[str] = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            re.X,
        )

        if re.fullmatch(ipv4_pattern, ip):
            self.__ip: str = ip
        else:
            raise ValueError("Invalid address.")

    def __str__(self):
        return self.__ip

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__ip!r})"

    def __len__(self):
        return len(self.__ip)


class ReceivingAddress:
    """
    A string wrapped to represent a receiving address for crypto-wallets.

    Raises ValueError if __init__ does not get passed a valid receiving address.\n
    Implements __str__, __repr__ and __len__.
    """

    def __init__(self, receiving_address: str):
        if receiving_address.isalnum() and len(receiving_address) == 34:
            self.__receiving_address: str = receiving_address
        else:
            raise ValueError("Invalid address.")

    def __str__(self):
        return self.__receiving_address

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__receiving_address!r})"

    def __len__(self):
        return len(self.__receiving_address)


class Genkey:
    """
    A string wrapped to represent a genkey for crypto-wallets.

    Raises ValueError if __init__ does not get passed a valid genkey.\n
    Implements __str__, __repr__ and __len__.
    """

    def __init__(self, genkey: str):
        if genkey.isalnum() and len(genkey) == 50:
            self.__genkey: str = genkey
        else:
            raise ValueError("Invalid genkey.")

    def __str__(self):
        return self.__genkey

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__genkey!r})"

    def __len__(self):
        return len(self.__genkey)


class Subid:
    """
    A string wrapped to represent a vultr subid.

    Raises ValueError if __init__ does not get passed a valid subid.\n
    Implements __str__, __repr__.
    """

    def __init__(self, subid: str):
        if subid.isdigit() and len(subid) == 6:
            self.__subid: str = subid
        else:
            raise ValueError("Invalid subid.")

    def __str__(self):
        return str(self.__subid)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__subid!r})"
