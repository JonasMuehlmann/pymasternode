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

"""Interact with the Vultr API or send commands to servers."""

import contextlib
import json
from pathlib import PosixPath
from typing import Dict, List, Union, Generator, Any, Optional

import gevent
import requests
from pssh.clients import ParallelSSHClient

from src import pymasternode, wallet
from src.helpers import (
    Command,
    Hostname,
    Ip,
    Path,
    Subid,
    call_until_returns_true,
    Label,
)

# noinspection PyTypeChecker
privkey: PosixPath = PosixPath(
    pymasternode.CONFIG["vps"]["ssh_privkey_path"]
).expanduser()

client: ParallelSSHClient = ParallelSSHClient(
    user="root",
    pkey=str(privkey),
    timeout=60,
    tunnel_timeout=60,
    num_retries=2,
    retry_delay=10,
)


class Instance:
    def __init__(self, label: Label) -> None:
        self._ip: Ip = None
        self._subid: Subid = None
        self._label: Label = label
        self._hostname: Hostname = Hostname(label)

    @property
    def ip(self) -> Ip:
        return self._ip

    @property
    def subid(self) -> Subid:
        return self._subid

    @property
    def label(self) -> str:
        return self._label

    @property
    def hostname(self) -> str:
        return self._hostname

    @ip.setter
    def ip(self, new_value: str) -> None:
        self._ip = Ip(new_value)

    @subid.setter
    def subid(self, new_value: str) -> None:
        self._subid = Subid(new_value)

    @label.setter
    def label(self, new_value: str) -> None:
        self._label = Label(new_value)

    @hostname.setter
    def hostname(self, new_value: str) -> None:
        self._hostname = Hostname(new_value)

    def get_host_arg(self) -> Optional[str]:  #
        """Returns the config-line belonging to the specified label."""
        with open(wallet.MODULE_SETTINGS["PATH_MN_CONF"], "r") as conf:
            for line in conf:
                if line.startswith(self.label):
                    return line.strip()

    # TODO: Adjust all docstrings
    def is_built(self) -> bool:
        """Check if all servers are activated.

        Args:
            instances (List[Subid]): Subids of servers to be checked

        Returns (bool):
            True if all servers are active, False otherwise

        """
        return pymasternode.VULTR.server.list(self.subid)

    def create(self, delay_return_until_built: bool = True, ) -> Subid:
        """Create new server instances.

        This function can be applied to just one, or multiple servers.

        Args:
            delay_return_until_all_built : IF True, do not return until all servers are built

        Returns:
            created_servers: Subids of the created servers

        """
        vps_settings: Union[str, int] = pymasternode.CONFIG["vps"]

        created_server = Subid(
            pymasternode.VULTR.server.create(
                vps_settings["location_id"],
                vps_settings["plan_id"],
                vps_settings["os_id"],
                vps_settings["ssh_keys"],
                vps_settings["script_id"],
                hostname=self.hostname,
                label=self.label,
            )["SUBID"]
        )

        if delay_return_until_built:
            call_until_returns_true(
                function_name=self.is_built(),
                function_parameters=created_server,
                call_interval_seconds=5.0,
            )

        return created_server

    def reboot(self) -> None:
        """Reboot specified servers.

        This function can be applied to just one, or multiple servers.

        Args:
            subids (List[int]): Subids, indicating servers to be rebooted

        """
        pymasternode.VULTR.server.reboot(self.subid)

    def destroy(self) -> None:
        """Destroy specified servers.

        This function can be applied to just one, or multiple servers.

        Args:
            subids (List[int]): Subids, indicating servers to be destroyed

        """
        pymasternode.VULTR.server.destroy(self.subid)

    def reinstall(self) -> None:
        pymasternode.VULTR.server.reinstall(self.subid)

    def command_print_outputs(self, output: Dict) -> None:
        """Print the output of sent commands.

        Args:
            output: Output object to print

        """
        for host, host_output in output.items():
            for line in host_output.stdout:
                print(f"Host [{host}] - {line}")
            for line in host_output.stderr:
                print(f"Host [{host}] - {line}")

    def command_send(
            self, commands: List[Command], host_args: List[Command] = None
    ) -> object:
        """Send list of commands to list of hosts.

        Args:
            commands: list of commands to send
            host_args: host specific commands

        Returns:
            object: A host output object

        """
        client.hosts = self.ip
        client.pool_size = len(self.ip)

        return client.run_command(
            command=" && ".join(commands), stop_on_errors=False, host_args=host_args
        )

    def send_files(self, path_from: Path, path_to: Path, is_dir: bool = False) -> None:
        """Send chosen file to multiple hosts in parallel.

        Args:
            path_from: Path of file to send
            path_to: Where on remote-hosts to send file to
            is_dir: Is file a directory?

        """
        client.hosts = self.ip
        client.pool_size = len(self.ip)

        greenlets: object = client.scp_send(str(path_from), str(path_to), is_dir)
        gevent.joinall(greenlets, raise_error=True)

    def pre_setup(self) -> None:
        """Download and execute pre-setup script on remote host.

        The script is expected to be pymasternode/data/pre_setup.sh

        Args:
            hosts: List of IP's of servers to send commands to

        """
        self.send_files(
            path_from=Path(__file__).parents[2] / "data" / "pre_setup.sh",
            path_to=Path("/root/pre_setup.sh"),
        )
        self.command_send(self.ip, ["chmod +x pre_setup.sh", "./pre_setup.sh"])

    def install_mn(self) -> None:
        """Download and execute MN install script on remote host.

        The script is expected to be pymasternode/data/mn_setup.sh

        Args:
            hosts: List of IP's of servers to send commands to

        """
        self.send_files(
            self.ip,
            Path(__file__).parents[1] / "data" / "mn_setup.sh",
            Path("/root/pre_setup.sh"),
        )
        host_arg = wallet.get_host_arg(self.label)
        self.command_send(["chmod +x mn_setup.sh", "./mn_setup.sh"], [host_arg])

    def is_synced(self, delay_return_until_synced: bool = True) -> bool:
        """Check if remote wallets are synced (+- 100 blocks).

        The remote block height will be specified as the minimum block height of all remote wallets.

        Args:
            delay_return_until_synced: if True, the function will not return unitl all instances are synced

        Returns:
            bool: True if synced, False otherwise

        """
        json_data = json.loads(
            requests.get(
                "https://explorer.globaltoken.org/api/status?q=getTxOutSetInfo"
            ).text
        )
        block_height_global: int = json_data["txoutsetinfo"]["height"]

        remote_block_heights: object = self.command_send(
            commands=[
                r"/root/globaltoken/bin/globaltoken-cli -getinfo | grep -Po '\"blocks\": *\K[0-9]*'"
            ],
        )
        min_remote_block_height = int(next(remote_block_heights[self.ip].stdout))

        if delay_return_until_synced:
            call_until_returns_true(
                function_name=self.is_synced,
                function_parameters=self.ip,
                call_interval_seconds=10.0,
            )
            return True

        return (min_remote_block_height + 100) >= block_height_global

    def complete_setup(
            self, label: Label = label, delay_return_until_synced: bool = True
    ) -> None:
        if self.ip is None:
            self.create(label)

        call_until_returns_true(self.is_built())
        self.pre_setup()
        self.install_mn()
        self.is_synced(delay_return_until_synced)


@contextlib.contextmanager
def setup_mn(label: Label) -> Generator[Instance, Any, None]:
    instance: Instance = Instance(label)
    yield instance


# def server_is_built(instances: List[Subid]) -> bool:
#     """Check if all servers are activated.
#
#     Args:
#         instances (List[Subid]): Subids of servers to be checked
#
#     Returns (bool):
#         True if all servers are active, False otherwise
#
#     """
#
#     return all(pymasternode.VULTR.server.list(instance) for instance in instances)
#
#
# def server_create(
#         host_names: List[Hostname], delay_return_until_all_built: bool = True
# ) -> List[Subid]:
#     """Create new server instances.
#
#     This function can be applied to just one, or multiple servers.
#
#     Args:
#         host_names: Hostnames/labels of to be created servers
#         delay_return_until_all_built : IF True, do not return until all servers are built
#
#     Returns:
#         created_servers: Subids of the created servers
#
#     """
#
#     vps_settings: Union[str, int] = pymasternode.CONFIG["vps"]
#
#     created_servers = [
#         Subid(
#             pymasternode.VULTR.server.create(
#                 vps_settings["location_id"],
#                 vps_settings["plan_id"],
#                 vps_settings["os_id"],
#                 vps_settings["ssh_keys"],
#                 vps_settings["script_id"],
#                 hostname=host_name,
#                 label=host_name,
#             )["SUBID"]
#         )
#         for host_name in host_names
#     ]
#
#     if delay_return_until_all_built:
#         call_until_returns_true(
#             function_name=server_is_built,
#             function_parameters=created_servers,
#             call_interval_seconds=5.0,
#         )
#
#     return created_servers
#
#
# def server_reboot(subids: List[Subid]) -> None:
#     """Reboot specified servers.
#
#     This function can be applied to just one, or multiple servers.
#
#     Args:
#         subids (List[int]): Subids, indicating servers to be rebooted
#
#     """
#
#     for subid in subids:
#         pymasternode.VULTR.server.reboot(subid)
#
#
# def server_destroy(subids: List[Subid]) -> None:
#     """Destroy specified servers.
#
#     This function can be applied to just one, or multiple servers.
#
#     Args:
#         subids (List[int]): Subids, indicating servers to be destroyed
#
#     """
#
#     for subid in subids:
#         pymasternode.VULTR.server.destroy(subid)
#
#
# def server_reinstall(subids: List[Subid]) -> None:
#     for subid in subids:
#         pymasternode.VULTR.server.reinstall(subid)
#
#
# # CHECK: If it would make sense to build a command class with the commmand itself as a member and the send and print output methods
# def command_print_outputs(output: Dict) -> None:
#     """Print the output of sent commands.
#
#     Args:
#         output: Output object to print
#
#     """
#
#     for host, host_output in output.items():
#         for line in host_output.stdout:
#             print(f"Host [{host}] - {line}")
#         for line in host_output.stderr:
#             print(f"Host [{host}] - {line}")
#
#
# def command_send(
#         hosts: List[Ip], commands: List[Command], host_args: List[Command] = None
# ) -> object:
#     """Send list of commands to list of hosts.
#
#     Args:
#         hosts: List of IP's of servers to send commands to
#         commands: list of commands to send
#         host_args: host specific commands
#
#     Returns:
#         object: A host output object
#
#     """
#
#     client.hosts = hosts
#     client.pool_size = len(hosts)
#
#     return client.run_command(
#         command=" && ".join(commands), stop_on_errors=False, host_args=host_args
#     )
#
#
# def send_files(
#         hosts: List[Ip], path_from: Path, path_to: Path, is_dir: bool = False
# ) -> None:
#     """Send chosen file to multiple hosts in parallel.
#
#     Args:
#         hosts: Hosts to send file to
#         path_from: Path of file to send
#         path_to: Where on remote-hosts to send file to
#         is_dir: Is file a directory?
#
#     """
#
#     client.hosts = hosts
#     client.pool_size = len(hosts)
#
#     greenlets: object = client.scp_send(str(path_from), str(path_to), is_dir)
#     gevent.joinall(greenlets, raise_error=True)
#
#
# def pre_setup(hosts: List[Ip]) -> None:
#     """Download and execute pre-setup script on remote host.
#
#     The script is expected to be pymasternode/data/pre_setup.sh
#
#     Args:
#         hosts: List of IP's of servers to send commands to
#
#     """
#
#     send_files(
#         hosts,
#         path_from=Path(__file__).parents[2] / "data" / "pre_setup.sh",
#         path_to=Path("/root/pre_setup.sh"),
#     )
#     command_send(hosts, ["chmod +x pre_setup.sh", "./pre_setup.sh"])
#
#
# def install_mn(hosts: List[Ip]) -> None:
#     """Download and execute MN install script on remote host.
#
#     The script is expected to be pymasternode/data/mn_setup.sh
#
#     Args:
#         hosts: List of IP's of servers to send commands to
#
#     """
#
#     send_files(
#         hosts,
#         Path(__file__).parents[1] / "data" / "mn_setup.sh",
#         Path("/root/pre_setup.sh"),
#     )
#     host_args = wallet.get_host_args(
#         database.get_info(
#             input_data=hosts, input_identifier="Ip", output_identifier="Label"
#         )
#     )
#     command_send(hosts, ["chmod +x mn_setup.sh", "./mn_setup.sh"], host_args)
#
#
# def is_synced(hosts: List[Ip], delay_return_until_all_synced: bool = True) -> bool:
#     """Check if remote wallets are synced (+- 100 blocks).
#
#     The remote block height will be specified as the minimum block height of all remote wallets.
#
#     Parameters:
#         hosts: List of hosts to check
#         delay_return_until_all_synced: if True, the function will not return unitl all instances are synced
#
#     Returns:
#         bool: True if synced, False otherwise
#
#     """
#
#     json_data = json.loads(
#         requests.get(
#             "https://explorer.globaltoken.org/api/status?q=getTxOutSetInfo"
#         ).text
#     )
#     block_height_global: int = json_data["txoutsetinfo"]["height"]
#
#     remote_block_heights: object = command_send(
#         hosts=hosts,
#         commands=[
#             r"/root/globaltoken/bin/globaltoken-cli -getinfo | grep -Po '\"blocks\": *\K[0-9]*'"
#         ],
#     )
#     min_remote_block_height = min(
#         int(next(remote_block_heights[host].stdout)) for host in hosts
#     )
#
#     if delay_return_until_all_synced:
#         call_until_returns_true(
#             function_name=is_synced,
#             function_parameters=hosts,
#             call_interval_seconds=10.0,
#         )
#         return True
#     else:
#         return (min_remote_block_height + 100) >= block_height_global


def main() -> None:
    pass
    # with setup_mn("FooBar") as mn:
    #     mn.complete_setup()


main()
#  send_commands_old(
#      hosts=database.get_all_ips(),
#      command="echo -e \"$(echo '* * * * * { cd /root/monitoring && ./watchdog.sh && date; }
#      >>/tmp/cron_watchdog.log 2>&1' ; crontab -l)\n\" | crontab - && crontab -l",
#  )
# send_commands_old(hosts=database.get_all_ips(), command="free -h | grep Swap | awk '{print $2}'")
