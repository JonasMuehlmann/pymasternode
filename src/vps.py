"""Interact with the Vultr API or send commands to servers."""
import json
from pathlib import PosixPath
from typing import Dict, List

import gevent
import requests
from pssh import exceptions
from pssh.clients import ParallelSSHClient

from src import pymasternode
from src.helpers import (Command, Hostname, Ip, Label, Path, Subid)


# noinspection PyTypeChecker
privkey: PosixPath = PosixPath(
    pymasternode.CONFIG["vps"]["ssh_privkey_path"]
).expanduser()


def server_create(host_names: List[Hostname]) -> List[Subid]:
    """
    Create new server instances.

    This function can be applied to just one, or multiple servers.

    Args:
        host_names: Hostnames/labels of to be created servers

    Returns:
        created_servers: Subids of the created servers

    """
    # TODO: Start server setup after server is ready.

    # noinspection PyTypeChecker
    location_id: int = int(pymasternode.CONFIG["vps"]["location_id"])
    # noinspection PyTypeChecker
    plan_id: int = int(pymasternode.CONFIG["vps"]["plan_id"])
    # noinspection PyTypeChecker
    os_id: int = int(pymasternode.CONFIG["vps"]["os_id"])
    # noinspection PyTypeChecker
    ssh_keys: str = str(pymasternode.CONFIG["vps"]["ssh_keys"])
    # noinspection PyTypeChecker
    script_id: int = int(pymasternode.CONFIG["vps"]["script_id"])

    created_servers: List[Subid] = []
    for host in host_names:
        hostname: Hostname = host
        label: Label = Label(host)
        created_servers.append(
            Subid(
                pymasternode.VULTR.server.create(
                    location_id, plan_id, os_id, ssh_keys, hostname, label, script_id
                )["SUBID"]
            )
        )
    return created_servers


def is_active(subids: List[Subid]) -> bool:
    """Check if all servers are activated.

    Args:
        subids (List[int]): Subids of servers to be checked

    Returns (bool):
        True if all servers are active, False otherwise

    """
    return all(pymasternode.VULTR.server.list(subid) for subid in subids)


def server_reboot(subids: List[Subid]) -> None:
    """Reboot specified servers.

    This function can be applied to just one, or multiple servers.

    Args:
        subids (List[int]): Subids, indicating servers to be rebooted

    """
    for subid in subids:
        pymasternode.VULTR.server.reboot(subid)


def server_reinstall(subids: List[Subid]) -> None:
    """Reinstall specified servers.

    This function can be applied to just one, or multiple servers.

    Args:
        subids (List[int]): Subids indicating servers to be reinstalled

    """
    for subid in subids:
        pymasternode.VULTR.server.reinstall(subid)


def send_commands_old(
    hosts: List[Ip],
    command: Command = None,
    mn_host_args: List[Command] = None,
    pre_setup: bool = False,
) -> None:
    """Send commands to a list of IP addresses.

    Parameters:
        hosts(List[str]): IP addresses to be worked on
        command (str): Custom command to be sent
        mn_host_args (List[str]): Host-based arguments, that will be applied to the mn setup
        pre_setup (bool): A flag used to decide if a pre-setup should be run (default is False)

    """
    # FIX: Adjust timeouts.
    client: ParallelSSHClient = ParallelSSHClient(
        hosts,
        user="root",
        pkey=str(privkey),
        timeout=60,
        tunnel_timeout=60,
        num_retries=2,
        retry_delay=10,
        pool_size=len(hosts),
    )

    def get_output() -> None:
        """Print the output of sent commands."""
        for host, host_output in output.items():
            for line in host_output.stdout:
                print("Host [%s] - %s" % (host, line))
            for line in host_output.stderr:
                print("Host [%s] - %s" % (host, line))

    if command is not None:
        try:
            output = client.run_command(command, stop_on_errors=False)
            get_output()
        except exceptions.AuthenticationException as error:
            print(error)
    # FIX: Handle ssh2.exceptions.SocketRecvError, which occurs when collecting output of rebooting serves.
    # TODO: Upload script to server and execute there.
    if pre_setup:
        pre_setup_script: Command = Command("")
        with open(
            pymasternode.PATH_PROJECT_ROOT / "data" / "pre_setup.sh", "r"
        ) as script:
            for line in script:
                if not line.strip() or line.startswith("#"):
                    pass
                else:
                    pre_setup_script += f"{line.strip()} && "
        if pre_setup_script.endswith(" && "):
            pre_setup_script = Command(pre_setup_script[:-4])
        output = client.run_command(pre_setup_script)
        get_output()
    # TODO: Upload script to server and execute there.
    if mn_host_args:
        mn_script: Command = Command("")
        with open(
            pymasternode.PATH_PROJECT_ROOT / "data" / "mn_setup.sh", "r"
        ) as script:
            for line in script:
                if line.strip() and not line.startswith("#"):
                    mn_script += f"{line.strip()} && "
                # if line.strip() and (not line.startswith("#")):
                #    mn_script += f"{line.strip()} && "
        if mn_script.endswith(" && "):
            mn_script = Command(mn_script[:-4])
        output = client.run_command(mn_script, host_args=mn_host_args)
        get_output()


def command_get_output(output: Dict) -> None:
    """Print the output of sent commands.

    Args:
        output: Output object to print
    """
    for host, host_output in output.items():
        for line in host_output.stdout:
            print("Host [%s] - %s" % (host, line))
        for line in host_output.stderr:
            print("Host [%s] - %s" % (host, line))


def command_send(
    hosts: List[Ip], commands: List[Command], host_args: List[Command] = None
) -> object:
    """Send list of commands to list of hosts.

    Args:
        hosts: List of IP's of servers to send commands to
        commands: list of commands to send
        host_args: host specific commands

    Returns:
        object: A host output object

    """
    client = ParallelSSHClient(
        hosts,
        user="root",
        pkey=str(privkey),
        timeout=60,
        tunnel_timeout=60,
        num_retries=2,
        retry_delay=10,
        pool_size=len(hosts),
    )
    command_string: Command = Command("")
    for command in commands:
        command_string += command + " && "

    return client.run_command(
        command=command_string[:-4], stop_on_errors=False, host_args=host_args
    )


def send_files(
    hosts: List[Ip], path_from: Path, path_to: Path, is_dir: bool = False
) -> None:
    """Send chosen file to multiple hosts in parallel.

    Args:
        hosts: Hosts to send file to
        path_from: Path of file to send
        path_to: Where on remote-hosts to send file to
        is_dir: Is file a directory?
    """
    client = ParallelSSHClient(
        hosts,
        user="root",
        pkey=str(privkey),
        timeout=60,
        tunnel_timeout=60,
        num_retries=2,
        retry_delay=10,
        pool_size=len(hosts),
    )
    greenlets: object = client.scp_send(str(path_from), str(path_to), is_dir)
    gevent.joinall(greenlets, raise_error=True)


def is_synced(hosts: List[Ip]) -> bool:
    """Check if remote wallets are synced (+- 100 blocks).
    The remote block height will be specified as the minimum block height of all remote wallets.

    Parameters:
        hosts: List of hosts to check

    Returns:
        bool: True if synced, False otherwise

    """
    json_data = json.loads(
        requests.get(
            "https://explorer.globaltoken.org/api/status?q=getTxOutSetInfo"
        ).text
    )
    block_height_global: int = json_data["txoutsetinfo"]["height"]

    command_output = command_send(
        hosts=hosts,
        commands=[
            Command(
                "/root/globaltoken/bin/globaltoken-cli -getinfo | grep -Po '\"blocks\": *\K[0-9]*'"
            )
        ],
    )
    min_remote_block_height = min(
        int(next(command_output[host].stdout)) for host in hosts
    )

    return (min_remote_block_height + 100) >= block_height_global


def install_mn(hosts: List[Ip], mn_host_args: List[Command]) -> None:
    """Download and execute MN install script on remote host.

    The script is expected to be pymasternode/data/mn_setup.sh

    Args:
        hosts: List of IP's of servers to send commands to
        mn_host_args: List of host specific arguments to use for host, has to match order of hosts
    """
    # CHECK: For way to remove hardcoded paths
    send_files(
        hosts,
        Path(__file__).parents[1] / "data" / "mn_setup.sh",
        Path("/root/pre_setup.sh"),
    )
    command_send(
        hosts, [Command("chmod +x mn_setup.sh"), Command("./mn_setup.sh")], mn_host_args
    )


def pre_setup(hosts: List[Ip]) -> None:
    """Download and execute pre-setup script on remote host.

    The script is expected to be pymasternode/data/pre_setup.sh

    Args:
        hosts: List of IP's of servers to send commands to

    """
    # CHECK: For way to remove hardcoded paths
    send_files(
        hosts,
        Path(__file__).parents[2] / "data" / "pre_setup.sh",
        Path("/root/pre_setup.sh"),
    )
    command_send(hosts, [Command("chmod +x pre_setup.sh"), Command("./pre_setup.sh")])


def main() -> None:
    pass


main()
#  send_files(
#      database.get_all_ips(),
#      "~/PycharmProjects/pymasternode/venv/pymasternode/monitoring/status_watchdog.py",
#      "/root/monitoring/status_watchdog.py",
#      False,
#  )


#  send_commands_old(
#      hosts=database.get_all_ips(),
#      command="echo -e \"$(echo '* * * * * { cd /root/monitoring && ./watchdog.sh && date; }
#      >>/tmp/cron_watchdog.log 2>&1' ; crontab -l)\n\" | crontab - && crontab -l",
#  )
# send_commands_old(hosts=database.get_all_ips(), command="free -h | grep Swap | awk '{print $2}'")
