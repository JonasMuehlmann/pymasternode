#!/usr/bin/env python3
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
