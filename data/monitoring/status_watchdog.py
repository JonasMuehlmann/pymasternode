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

# !/usr/bin/env python3

import json
import subprocess

from . import telegram_bot

last_status = ""
current_status = ""

with open("/root/monitoring/last_status.txt", "r") as f:
    last_status = f.read()

HOSTNAME = subprocess.run(  # noqa: S607
    "hostname", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
).stdout.decode("utf-8")

try:
    status_json = subprocess.run(
        ["/root/globaltoken/bin/globaltoken-cli", "masternode", "status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        encoding="utf-8",
    )
    current_status = json.loads(status_json.stdout.decode("utf-8"))["status"]

except (subprocess.CalledProcessError, json.decoder.JSONDecodeError) as e:
    print("Error getting status")
    telegram_bot.send_message("Error getting status on {}".format(HOSTNAME))

if last_status not in ("", current_status):
    telegram_bot.send_message(
        "Status change from {} to {} on {}".format(
            last_status, current_status, HOSTNAME
        )
    )
with open("/root/monitoring/last_status.txt", "w") as f:
    f.write(current_status)
