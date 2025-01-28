# copyright github.com/devgaganin

from os import getenv

API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")
COOKIES = getenv("AUTH_CODE", "")
OWNER_ID = getenv("OWNER_ID", "1213121") # if want to make accessible in channel put channel id in owner id field
