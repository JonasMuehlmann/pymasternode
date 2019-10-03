"""Interact with a database, that stores server identification info."""
# TODO: Create table for each coin.
import sqlite3
from sqlite3.dbapi2 import Connection, Cursor
from typing import Iterable, List

from src import pymasternode
from src.helpers import Identifier, Ip, Label, Subid


DB: Connection = sqlite3.connect(
    pymasternode.PATH_PROJECT_ROOT / "data" / "server_info.db"
)
C: Cursor = DB.cursor()


def load_data() -> None:
    """Update database of server info."""
    response: Iterable = pymasternode.VULTR.server.list()
    subids: List[Subid] = [Subid(response[i]["SUBID"]) for i in response]
    ips: List[Ip] = [response[i]["main_ip"] for i in response]
    labels: List[Label] = [response[i]["label"] for i in response]

    C.execute("DELETE FROM servers")
    C.executemany("INSERT INTO servers VALUES(?, ?, ?)", zip(subids, ips, labels))
    DB.commit()


def get_info(
    input_data: List[Identifier],
    input_identifier: str = "Subid",
    output_identifier: str = "Ip",
) -> List[Identifier]:
    """
    Take input values of type input_type and returns output of type output_identifier.

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
    results: List[Identifier] = []
    for element in input_data:
        C.execute(
            f"SELECT {output_identifier} FROM servers WHERE {input_identifier} = ?",
            (element,),
        )
        results.append(C.fetchone()[0])
    return results


def get_all_ips() -> List[Ip]:
    """
    Create a list of all server IP's.

    Returns:
        All server IP's

    """
    C.execute("SELECT ip FROM servers")
    query_output = C.fetchall()
    return [row[0] for row in query_output]


def main() -> None:
    load_data()


main()
