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

"""Interact with a database that stores server identification info."""
# TODO: Create table for each coin.

import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
from typing import Iterable, List

from src import pymasternode
from src.helpers import Identifier, Ip, Label, Subid

DB: Connection = sqlite3.connect(
    pymasternode.PATH_PROJECT_ROOT / "data" / "server_info.db"
)
curs: Cursor = DB.cursor()


# CHECK: If it makes sense to create a database class and use the load_data function as a constructor
def load_data() -> None:
    """Update database of server info."""
    response: Iterable = pymasternode.VULTR.server.list()
    subids: List[Subid] = [response[i]["SUBID"] for i in response]
    ips: List[Ip] = [response[i]["main_ip"] for i in response]
    labels: List[Label] = [response[i]["label"] for i in response]

    curs.execute("DELETE FROM servers")
    curs.executemany("INSERT INTO servers VALUES(?, ?, ?)", zip(subids, ips, labels))
    DB.commit()


def get_info(
        input_data: Identifier,
        input_identifier: str = "Subid",
        output_identifier: str = "Ip",
) -> Identifier:
    """Take input values of type input_type and returns output of type output_identifier.

    Identifiers:
        Label (str): The servers label/hostname

        Ip (str): The servers IP address

        Subid (int): The servers subid (used by the Vultr API)

    Args:
        input_data: Input values of type input_type
        input_identifier: The type of the input
        output_identifier:  The type of the output

    Returns:
        Alternative identifications for the input_data

    """
    curs.execute(
        f"SELECT {output_identifier} FROM servers WHERE {input_identifier} = ?",
        (input_data,),
    )
    return curs.fetchone()[0]


# REFACTOR: Rename to get_all and use parameter to decide what to get
def get_all_ips() -> List[Ip]:
    """Create a list of all server IP's.

    Returns:
        All server IP's

    """
    curs.execute("SELECT ip FROM servers")
    query_output = curs.fetchall()
    return [row[0] for row in query_output]


def main() -> None:
    load_data()


main()
