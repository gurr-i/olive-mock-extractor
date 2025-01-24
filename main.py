# Copyright github.com/devgaganin

import os
import requests
from telethon import TelegramClient, events
from telethon.tl.types import InputFile
from config import API_ID, API_HASH, BOT_TOKEN, AUTH_CODE

# Initialize the Telethon client
bot = TelegramClient("testbook_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Base URL for fetching test data
API_URL = "https://api.testbook.com/api/v2/tests/{test_id}"

# Temporary storage for test data
temp_data = {}
import html


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    """Handle /start command"""
    await event.reply(
        "Welcome to the Testbook Bot! Use the command `/fetch <test_id>` to fetch test data.\n"
        "Example: `/fetch 66fbeee4d8b88b617b0e69ab`"
    )


@bot.on(events.NewMessage(pattern="/fetch (.+)"))
async def get_test(event):
    """Handle /get_test command"""
    test_id = event.pattern_match.group(1)
    url = API_URL.format(test_id=test_id)
    params = {
        "auth_code": AUTH_CODE,
        "X-Tb-Client": "web,1.2",
        "language": "English",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("success", False):
            await event.reply("Failed to fetch test data. Please check the test ID.")
            return

        # Save data and prompt the user to select a language
        temp_data[event.chat_id] = data
        await event.reply(
            "Test data fetched successfully!\nPlease select a language:\n\n"
            "`/language en` - English\n"
            "`/language hn` - Hindi"
        )
    except Exception as e:
        pass


@bot.on(events.NewMessage(pattern="/language (.+)"))
async def select_language(event):
    """Handle language selection"""
    language = event.pattern_match.group(1)
    if language not in ["en", "hn"]:
        await event.reply("Invalid language! Please choose `/language en` or `/language hn`.")
        return

    data = temp_data.get(event.chat_id)
    if not data:
        await event.reply("No test data available. Use `/get_test <test_id>` first.")
        return

    # Generate the HTML file
    try:
        html_content = generate_html(data["data"], language)
        file_path = f"test_questions_{event.chat_id}.html"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        # Send the HTML file to the user
        await bot.send_file(event.chat_id, file=file_path, caption="__**Powered by Team SPY**__")
        os.remove(file_path)  # Clean up
    except Exception as e:
        await event.reply(f"Error generating HTML file: {e}")


def generate_html(data, language):
    """Generate visually appealing HTML content for the test with enhanced CSS, including 'comp'."""
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{html.unescape(data.get("title", "Test Questions"))}</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Roboto', sans-serif;
                    background-color: #f4f4f9;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #fff;
                    border-radius: 8px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    text-align: center;
                    color: #4caf50;
                }}
                h2 {{
                    text-align: center;
                    color: #2196f3;
                    font-size: 1.2rem;
                }}
                .question-box {{
                    margin: 20px 0;
                    padding: 15px;
                    background: #e8f5e9;
                    border-left: 5px solid #4caf50;
                    border-radius: 8px;
                }}
                .question-box h3 {{
                    margin: 0;
                    font-size: 1.2rem;
                    color: #333;
                }}
                .question-box .comp {{
                    font-size: 1rem;
                    color: #555;
                    margin-bottom: 10px;
                    padding: 10px;
                    background: #f9f9f9;
                    border-left: 4px solid #2196f3;
                    border-radius: 5px;
                }}
                .options {{
                    list-style-type: none;
                    padding: 0;
                    margin: 10px 0 0;
                }}
                .options li {{
                    margin: 5px 0;
                    padding: 10px 15px;
                    background: #fff;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.3s, border-color 0.3s;
                }}
                .options li:hover {{
                    background: #e3f2fd;
                    border-color: #2196f3;
                }}
                footer {{
                    text-align: center;
                    margin-top: 20px;
                    font-size: 0.8rem;
                    color: #999;
                }}
            </style>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
        </head>
        <body>
        <div class="container">
            <h1>{html.unescape(data.get("title", "Untitled Test"))}</h1>
            <h2>Course: {html.unescape(data.get("course", "Unknown Course"))}</h2>
        """

        # Process sections and questions
        for section in data.get("sections", []):
            section_title = html.unescape(section.get("title", "Untitled Section"))
            html_content += f"<h3>Section: {section_title}</h3>"
            for i, question in enumerate(section.get("questions", []), start=1):
                question_text = html.unescape(question.get(language, {}).get("value", "No Question Text Available"))
                comp_text = question.get(language, {}).get("comp")  # Get the 'comp' field if available
                # Fix image URLs
                question_text = fix_image_urls(question_text)
                comp_text = fix_image_urls(html.unescape(comp_text)) if comp_text else None
                
                html_content += f"""
                <div class="question-box">
                    <h3>Question {i}:</h3>
                """
                if comp_text:
                    html_content += f"""<div class="comp">{comp_text}</div>"""
                html_content += f"<p>{question_text}</p><ul class='options'>"
                
                # Render options
                for option in question.get(language, {}).get("options", []):
                    option_value = html.unescape(option.get("value", "No Option Text"))
                    option_value = fix_image_urls(option_value)
                    html_content += f"<li>{option_value}</li>"
                html_content += "</ul></div>"

        # Close container and body
        html_content += """
        </div>
        <footer>
            Powered by Test Generator Bot
        </footer>
        </body>
        </html>
        """

        return html_content

    except Exception as e:
        raise ValueError(f"Error generating HTML: {e}")


def fix_image_urls(text):
    """Fix image URLs that start with //storage.googleapis.com."""
    if "//storage.googleapis.com" in text:
        text = text.replace("//storage.googleapis.com", "https://storage.googleapis.com")
    return text




if __name__ == "__main__":
    print("Bot is running...")
    bot.run_until_disconnected()

# no part of this code/edits is allowed to use for commercial / sale purposes
