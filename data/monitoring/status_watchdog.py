#!/usr/bin/env python3
import json
import subprocess

from telegram_bot import send_message


last_status = ""
current_status = ""

with open("/root/monitoring/last_status.txt", "r") as f:
    last_status = f.read()

HOSTNAME = subprocess.run("hostname", stdout=subprocess.PIPE).stdout.decode("utf-8")

try:
    status_json = subprocess.run(
        ["/root/globaltoken/bin/globaltoken-cli", "masternode", "status"],
        stdout=subprocess.PIPE,
        check=True,
    )
    current_status = json.loads(status_json.stdout.decode("utf-8"))["status"]

except (subprocess.CalledProcessError, json.decoder.JSONDecodeError) as e:
    print("Error getting status")
    send_message("Error getting status on {}".format(HOSTNAME))

if last_status not in ("", current_status):
    send_message(
        "Status change from {} to {} on {}".format(
            last_status, current_status, HOSTNAME
        )
    )
with open("/root/monitoring/last_status.txt", "w") as f:
    f.write(current_status)
