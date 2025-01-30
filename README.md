# Olive Mock Extractor Bot

A Telegram bot built using the Telethon library, designed to fetch and process mock test questions and solutions from Oliveboard. The bot provides an automated interface for users to extract and submit test papers directly through Telegram.

## Features

- **Command Handling**: Use the `/fetch` command to retrieve mock test papers by specifying the exam type and test ID.
- **Exam Types Supported**: Supports a variety of mock test categories, including SSC, RRB, and NTPC exams.
- **HTML Parsing**: Processes and modifies HTML content using BeautifulSoup for better readability and storage.
- **Automated Test Submission**: Submits tests programmatically to generate solutions.
- **Solution Retrieval**: Fetches and modifies solution pages for distribution.
- **File Management**: Saves test papers and solutions locally and uploads them directly to Telegram.

---

## How to Use

1. **Start the Bot**: Use the `/start` command to initialize the bot.
2. **Fetch a Test**: Run `/fetch exam testid` (e.g., `/fetch ntpc1 1`) to retrieve the desired test paper.
3. **Receive Output**: The bot will send the modified test paper and solution as downloadable files.

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/olive-mock-extractor.git
   cd olive-mock-extractor
   ```

2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `config.py` file with the following constants:
   ```python
   API_ID = "your_api_id"
   API_HASH = "your_api_hash"
   BOT_TOKEN = "your_bot_token"
   COOKIES = "your_session_cookies"
   OWNER_ID = your_telegram_user_id
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

---

## Key Components

- **Bot Initialization**: Uses the `Telethon` library for creating a Telegram bot client.
- **Command Handling**: Processes commands using regex-based message patterns.
- **Web Scraping**: Retrieves and modifies test HTML and solution pages via `requests` and `BeautifulSoup`.
- **File Management**: Handles saving and cleanup of generated files.

---

## Technologies Used

- Python
- Telethon
- Requests
- BeautifulSoup (bs4)

---

## Future Enhancements

- Support for additional exam platforms.
- Improved error handling and user feedback.
- Cloud storage for test papers and solutions.
- Bot deployment on cloud platforms for 24/7 availability.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
