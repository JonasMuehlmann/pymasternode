# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import time
from collections import namedtuple, defaultdict
from pathlib import PosixPath
from typing import Pattern, Union, Callable, Any, List, Iterable, Type, Dict, NewType

Path = PosixPath
Label = str
Hostname = str
Command = str
Identifier = Union["Label", "Ip", "Subid"]
OccurrenceStats = NewType("OccurrenceStats", Type[tuple])


def count_successive_repetitions(iterable: Iterable, wanted: Any) -> OccurrenceStats:
    """Count the first, last, least and most times 'wanted' appeared in 'iterable'.


    Args:
        iterable: An iterator to search in
        wanted: An item to count

    Returns:
        occurrence_stats: A namedtuple with the following fields: first, last, least, most and values


    'OccurrenceStats' contains the following fields:
        first: Successive repetitions in the first 'chain'

        last: Successive repetitions in the last 'chain'

        least: Smallest number of successive repetitions

        most: Highest number of successive repetitions

        values: A list containing all counts


    Example:
        >>> stats = count_successive_repetitions("F#o####oo###", "#")
        >>> print(stats.first)
            1
        >>> print(stats.last)
            3
        >>> print(stats.least)
            1
        >>> print(stats.most)
            4
        >>> print(stats.values)
            [1,4,3]

        If 'wanted' is not found once, 'OccurrenceStats' will contain a lone 0.

        >>> stats = count_successive_repetitions("Foo", "#")
        >>> print(stats.values)
            [0]

        If you want to count how many times a specific value of a mapping is repeated,
        you have to pass a view of the values for 'iterable'.

        >>> example_dict = {
                "Foo": "#",
                "Fooo": "Bar",
                "Foooo": "#",
                "Fooooo": "#",
                "Foooooo": "Bar",
                "Fooooooo": "#",
            }

        >>> stats = count_successive_repetitions(example_dict.values(), "#")
        >>> print(stats.values)
            [1, 2, 1]

    """
    count: int = 0
    last: Any = None
    occurrences: Dict[int, int] = defaultdict(int, {0: 0})

    for item in iterable:  # noqa: VNE002
        if item == wanted:
            occurrences[count] += 1
        elif last == wanted:
            count += 1

        last = item

    # noinspection PyShadowingNames
    occurrence_stats: Type[tuple] = namedtuple(
        "OccurrenceStats", ["first", "last", "least", "most", "values"]
    )

    return occurrence_stats(
        list(occurrences.values())[0],
        list(occurrences.values())[-1],
        min(occurrences.values()),
        max(occurrences.values()),
        list(occurrences.values()),
    )


def call_until_returns_true(
        function_name: Callable[[Any], Any],
        function_parameters: List[Any] = None,
        call_interval_seconds: float = 10.0,
) -> None:
    while not function_name(*function_parameters):
        time.sleep(call_interval_seconds)


class Ip:
    """A string wrapped to represent an IPv4 address.

    Raises ValueError if __init__ does not get passed a valid address.

    Implements __str__, __repr__ and __len__.

    """

    def __init__(self, ip: str) -> None:
        ipv4_pattern: Pattern[str] = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            re.X,
        )

        if re.fullmatch(ipv4_pattern, ip):
            self.ip: str = ip
        else:
            raise ValueError("Invalid address.")

    def __str__(self) -> str:
        return self.ip

    def __len__(self) -> int:
        return len(self.ip)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.ip}"


class ReceivingAddress:
    """A string wrapped to represent a receiving address for crypto-wallets.

    Raises ValueError if __init__ does not get passed a valid receiving address.

    Implements __str__, __repr__ and __len__.

    """

    def __init__(self, receiving_address: str) -> None:
        if receiving_address.isalnum() and len(receiving_address) == 34:
            self.receiving_address: str = receiving_address
        else:
            raise ValueError("Invalid address.")

    def __str__(self) -> str:
        return self.receiving_address

    def __len__(self) -> int:
        return len(self.receiving_address)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.receiving_address}"


class Genkey:
    """A string wrapped to represent a genkey for crypto-wallets.

    Raises ValueError if __init__ does not get passed a valid genkey.

    Implements __str__, __repr__ and __len__.

    """

    def __init__(self, genkey: str) -> None:
        if genkey.isalnum() and len(genkey) == 50:
            self.genkey: str = genkey
        else:
            raise ValueError("Invalid genkey.")

    def __str__(self) -> str:
        return self.genkey

    def __len__(self) -> int:
        return len(self.genkey)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.genkey}"


class Subid:
    """A string wrapped to represent a vultr subid.

    Raises ValueError if __init__ does not get passed a valid subid.

    Implements __str__, __repr__.

    """

    def __init__(self, subid: str) -> None:
        if subid.isdigit() and len(subid) == 8:
            self.subid: str = subid
        else:
            raise ValueError("Invalid subid.")

    def __str__(self) -> str:
        return str(self.subid)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:{self.subid}"
