import os
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputFile
from config import API_ID, API_HASH, BOT_TOKEN, COOKIES, OWNER_ID
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Initialize the Telethon client
bot = TelegramClient("olive_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    """Handle /start command"""
    await event.reply(
        "**Welcome to the Olive Mock Extractor Bot!**\n\n"
        "Send `/fetch exam testid` for oliveboard\n\n"
        "**__Example: `/fetch ntpc1 1`__**\n\n"
        "__**Powered by @Gurveer**__"
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
    # if event.sender_id != OWNER_ID:
    #     await event.reply("Not allowed")
    #     return
    
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
        await event.respond(f"**📕 Exam Name: {exam}**\n**🆔 Test ID: {test_id}**\n**🥹 Type: Question**\n\n__**Powered by @Gurveer**__", file=file_name)
        await prog.edit("Auto Submitting the test")
        submit_test(url, test_id, exam)
        await prog.edit("Test Submitted Successfully... ")

        # Generating the solution URL
        solution_url = url.replace("https://u1.oliveboard.in/exams/tests/", "https://u1.oliveboard.in/exams/solution/index3.php")
        print(solution_url)
        
        # Fetch the solution and modify HTML
        solution_content = fetch_solution(solution_url)
        await prog.edit("Trying to fetch the solution... ")

        mod_html = modify_html(solution_content, url)

        file_sol_name = f"solution_exam_{exam}_{test_id}.html"
        with open(file_sol_name, "w", encoding="utf-8") as file:
            file.write(mod_html)

        await prog.edit("Uploading Solution... ")
        await event.respond(f"**📕 Exam Name: {exam}**\n**🆔 Test ID: {test_id}**\n**🥹 Type: Solution**\n\n__**Powered by @Gurveer**__", file=file_sol_name)
        await prog.delete()

        # Clean up files after sending
        # os.remove(file_name)
        # if os.path.exists(file_sol_name):
        #     os.remove(file_sol_name)

    except requests.exceptions.RequestException as e:
        await event.respond(f"Failed to fetch the test details: {e}")

def submit_test(url, test_id, exam):
    surl = "https://u1.oliveboard.in/exams/tests/p/submittestfull.cgi"
    
    # Define headers with appropriate User-Agent and cookies
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": COOKIES,  # Ensure COOKIES is defined and valid
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

    # Format the q_value by appending "001" to the test_id (check if this is required)
    q_value = f"{test_id}001"
    print(f"q_value: {q_value}")

    # Construct the raw data payload for the submission
    raw_data = f"data=%7B%22{q_value}001%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2201%3A30%3A00%22%2C%22end%22%3A%2201%3A29%3A58%22%7D%5D%2C%22o%22%3A%22%22%7D%2C%22{q_value}002%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A57%22%2C%22end%22%3A%2200%3A59%3A53%22%7D%5D%2C%22o%22%3A%221%22%7D%2C%22{q_value}003%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A53%22%2C%22end%22%3A%2200%3A59%3A47%22%7D%5D%2C%22o%22%3A%22%22%7D%2C%22{q_value}004%22%3A%7B%22q%22%3A%22{q_value}%22%2C%22t%22%3A%5B%7B%22st%22%3A%2200%3A59%3A47%22%2C%22end%22%3A%2200%3A59%3A46%22%7D%2C%7B%22st%22%3A%2200%3A59%3A46%22%2C%22end%22%3A%2200%3A59%3A43%22%7D%5D%2C%22o%22%3A%22%22%7D%7D&uid=&qpi={test_id}&ppi=-1&lang=eqt&c={exam}&source=web"
    print(f"Raw data: {raw_data}")

    # Send the POST request to submit the test
    try:
        response = requests.post(surl, headers=headers, data=raw_data)

        # Check if the submission was successful
        if response.status_code == 200:
            print("Test submitted successfully!")
            print(f"Response: {response.text}")
        else:
            print(f"Failed to submit the test. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during submission: {e}")

# Function to sanitize the filename by removing query parameters
def sanitize_filename(url):
    return os.path.basename(url.split('?')[0])


def fetch_solution(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": COOKIES,
        "Host": "u1.oliveboard.in",
        "Referer": "https://u1.oliveboard.in/",  # Add Referer header
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
    
    # Parse the HTML to extract CSS links
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Create a directory to store CSS files
    css_dir = "css_files"
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
    
    # Find all link tags with rel="stylesheet"
    css_links = soup.find_all("link", rel="stylesheet")
    
    # Download each CSS file
    for link in css_links:
        css_url = link.get("href")
        if css_url:
            # Resolve relative URLs
            css_url = urljoin(url, css_url)
            css_file_name = os.path.join(css_dir, os.path.basename(css_url))
            try:
                css_response = requests.get(css_url)
                css_file_name = sanitize_filename(css_file_name)
                with open(css_file_name, "wb") as f:
                    f.write(css_response.content)
                print(f"Downloaded CSS: {css_file_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download CSS file {css_url}: {e}")
    
    # Now, inject the local CSS file paths into the HTML
    for link in css_links:
        css_url = link.get("href")
        if css_url:
            # Replace the href attribute with the local path
            local_css_path = os.path.join(css_dir, os.path.basename(css_url))
            link["href"] = local_css_path

    # Convert the modified soup back to HTML
    modified_html = str(soup)

    return modified_html


def modify_html(html, full_url):
    """
    Modifies the HTML content by appending the appropriate base URL
    to relative links for 'href' and 'src' attributes.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Modify all 'href' and 'src' attributes to be absolute URLs
    for tag in soup.find_all(['a', 'img', 'script', 'link']):
        if tag.get('href'):
            # Resolve relative URLs
            if not tag['href'].startswith(('http://', 'https://')):
                if tag['href'].startswith('/'):
                    tag['href'] = urljoin('https://u1.oliveboard.in', tag['href'])
                else:
                    tag['href'] = urljoin(full_url, tag['href'])
        if tag.get('src'):
            # Resolve relative URLs
            if not tag['src'].startswith(('http://', 'https://')):
                if tag['src'].startswith('/'):
                    tag['src'] = urljoin('https://u1.oliveboard.in', tag['src'])
                else:
                    tag['src'] = urljoin(full_url, tag['src'])
    
    return str(soup)

# Run the bot
print("Bot started...")
bot.run_until_disconnected()