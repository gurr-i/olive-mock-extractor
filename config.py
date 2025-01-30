from os import getenv

# API_URL = getenv("API_URL", "https://api.testbook.com/api/v2/tests/{test_id}")

API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")
COOKIES = getenv("AUTH_CODE", "")
OWNER_ID = getenv("OWNER_ID", "") # if want to make accessible in channel put channel id in owner id field