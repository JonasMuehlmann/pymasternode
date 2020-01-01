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

import requests

with open("/root/monitoring/api_key&chatId_telegram.txt", "r") as f:
    token = f.readline().strip()
    chatId = f.readline().strip()


def send_message(message):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(
        token, chatId, message
    )
    response = requests.get(url)

    return response.json()
