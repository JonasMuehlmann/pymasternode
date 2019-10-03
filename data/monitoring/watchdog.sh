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
