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

#!/usr/bin/env bash

if pgrep globaltokend >/dev/null 2>&1; then
  :

else
  /root/globaltoken/bin/globaltokend
  python3 -c "import telegram_bot; telegram_bot.send_message('Remote wallet restart on $(hostname).')"
fi
python3 -c "import telegram_bot; import status_watchdog"

if (($(wc -l /tmp/cron_watchdog.log | awk '{print $1}') >= 10000)); then
  sed -i 1d /tmp/cron_watchdog.log
fi
