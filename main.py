# Copyright github.com/devgaganin

import os
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputFile
from config import API_ID, API_HASH, BOT_TOKEN, COOKIES, OWNER_ID
import re
from bs4 import BeautifulSoup

# Initialize the Telethon client
bot = TelegramClient("olive_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    """Handle /start command"""
    await event.reply(
        "**Welcome to the Mock Extractor Bot!**\n\n"
        "Send `/fetch exam testid` for oliveboard\n\n"
        "**__Example: `/fetch ntpc1 1`__**\n\n"
        "__**Powered by Team SPY**__"
    )

# --- OLIVEBOARD ---

# Headers for HTTP requests
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": COOKIES,
    "Host": "u1.oliveboard.in",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


# Base URIs for different exam types
BASE_URIS = {
    "cgl1": "https://u1.oliveboard.in/exams/tests/?c=ssc2019&testid={test_id}",
    "chsl": "https://u1.oliveboard.in/exams/tests/?c=chsl&testid={test_id}",
    "chsl2": "https://u1.oliveboard.in/exams/tests/?c=chsl2&testid={test_id}",
    "sscmts": "https://u1.oliveboard.in/exams/tests/?c=sscmts&testid={test_id}",
    "ntpc1": "https://u1.oliveboard.in/exams/tests/?c=ntpc1&os=1&testid={test_id}",
    "ntpc2": "https://u1.oliveboard.in/exams/tests/?c=ntpc2&os=1&testid={test_id}",
    "rrbalp1": "https://u1.oliveboard.in/exams/tests/?c=rrbalp1&os=1&testid={test_id}",
    "rrbalp2": "https://u1.oliveboard.in/exams/tests/?c=rrbalp2&os=1&testid={test_id}",
    "rrbgrpd": "https://u1.oliveboard.in/exams/tests/?c=rrbgrpd&os=1&testid={test_id}",

}

@bot.on(events.NewMessage(pattern=r"/fetch (\w+) (\d+)"))
async def fetch_exam(event):
    """Fetches test details based on the exam type and test ID."""
    if event.sender_id != OWNER_ID:
        await event.reply("Not allowed")
        return
    exam = event.pattern_match.group(1).lower()
    test_id = event.pattern_match.group(2)

    if exam not in BASE_URIS:
        await event.respond("Invalid exam type! Supported types are: " + ", ".join(BASE_URIS.keys()))
        return

    # Construct the URL
    url = BASE_URIS[exam].format(test_id=test_id)

    try:
        # Fetch the HTML content
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        html_content = response.text
        modified_html = modify_html(html_content, url)

        # Save the modified HTML to a file
        file_name = f"exam_{exam}_{test_id}.html"
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(modified_html)

        prog = await bot.send_message(event.chat_id, "Extracting Questions")

        # Send the file back to the user
        await prog.edit("Uploading Test Papers... ")
        await event.respond(f"**📕 Exam Name: {exam}**\n**🆔 Test ID: {test_id}**\n**🥹 Type: Question**\n\n__**Powered by Team SPY**__", file=file_name)
        await prog.edit("Auto Submitting the test")
        submit_test(url)
        await prog.edit("Test Submitted Sucessfully... ")
        t = url.replace("https://u1.oliveboard.in/exams/tests/", "https://u1.oliveboard.in/exams/solution/index3.php")
        print(t)
        k = fetch_solution(t)
        await prog.edit("Trying to fetch the solution... ")
        mod_html = mody_html(k, url)

        file_sol_name = f"solution_exam_{exam}_{test_id}.html"
        with open(file_sol_name, "w", encoding="utf-8") as file:
            file.write(mod_html)

        await prog.edit("Uploading Solution... ")
        await event.respond(f"**📕 Exam Name: {exam}**\n**🆔 Test ID: {test_id}**\n**🥹 Type: Solution**\n\n__**Powered by Team SPY**__", file=file_sol_name)
        await prog.delete()

        os.remove(file_name)
        if file_sol_name:
            os.remove(file_sol_name)

    except requests.exceptions.RequestException as e:
        await event.respond(f"Failed to fetch the test details: {e}")

def submit_test(url, test_id, exam):
    surl = "https://u1.oliveboard.in/exams/tests/p/submittestfull.cgi"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": COOKIES,
        "Host": "u1.oliveboard.in",
        "Origin": "https://u1.oliveboard.in",
        "Referer": url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
    }
    # Formatting q as "test_id001"
    q_value = f"{test_id}001"
    print(q_value)
    raw_data = f"data=%7B%22{q_value}001%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2201%3A30%3A00%22%2C%22end%22%3A%2201%3A29%3A58%22%7D%5D%2C%22o%22%3A%22%22%7D%2C%22{q_value}002%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A57%22%2C%22end%22%3A%2200%3A59%3A53%22%7D%5D%2C%22o%22%3A%221%22%7D%2C%22{q_value}003%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A53%22%2C%22end%22%3A%2200%3A59%3A47%22%7D%5D%2C%22o%22%3A%22%22%7D%2C%22{q_value}004%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A47%22%2C%22end%22%3A%2200%3A59%3A46%22%7D%2C%7B%22st%22%3A%2200%3A59%3A46%22%2C%22end%22%3A%2200%3A59%3A43%22%7D%5D%2C%22o%22%3A%22%22%7D%7D&uid=&qpi={test_id}&ppi=-1&lang=eqt&c={exam}&source=web"
    print(payload)
    response = requests.post(surl, headers=headers, data=raw_data)
    print(f"Test Submission Response Status Code: {response.status_code}")


# Step 2: Fetch Solution
def fetch_solution(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": COOKIES,
        "Host": "u1.oliveboard.in",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    print(f"Solution Fetch Response Status Code: {response.status_code}")
    return html_content

from bs4 import BeautifulSoup
from urllib.parse import urljoin

DEFAULT_BASE_URL = "https://u1.oliveboard.in/exams/tests/"

def modify_html(html, full_url):
    """
    Modifies the HTML content by appending the appropriate base URL
    to relative links for 'href' and 'src' attributes.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["a", "img", "link", "script"]):
        # Handle 'href' attribute for <a> and <link> tags
        if tag.has_attr("href"):
            if not tag["href"].startswith("http"):  # Only modify relative links
                tag["href"] = urljoin(DEFAULT_BASE_URL, tag["href"])

        # Handle 'src' attribute for <img> and <script> tags
        if tag.has_attr("src"):
            if not tag["src"].startswith("http"):  # Only modify relative sources
                tag["src"] = urljoin(DEFAULT_BASE_URL, tag["src"])

    return soup.prettify()


SOLUTION_BASE_URL = "https://u1.oliveboard.in/exams/solution/"

def mody_html(html, full_url):
    """
    Modifies the HTML content by appending the appropriate base URL
    to relative links for 'href' and 'src' attributes.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["a", "img", "link", "script"]):
        # Handle 'href' attribute for <a> and <link> tags
        if tag.has_attr("href"):
            if not tag["href"].startswith("http"):  # Only modify relative links
                tag["href"] = urljoin(SOLUTION_BASE_URL, tag["href"])

        # Handle 'src' attribute for <img> and <script> tags
        if tag.has_attr("src"):
            if not tag["src"].startswith("http"):  # Only modify relative sources
                tag["src"] = urljoin(SOLUTION_BASE_URL, tag["src"])

    return soup.prettify()

# Run the bot
print("Bot started...")
bot.run_until_disconnected()

# Copyright github.com/devgaganin
# no part of this code/edits is allowed to use for commercial / sale purposes
