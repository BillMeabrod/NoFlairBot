# NoFlairBot

A Reddit bot that monitors a subreddit and responds to users who post without user flair. The bot uses AI to generate witty, trash-talking responses to encourage users to add flair.

## Prerequisites

- Python 3.7 or higher
- A Reddit account
- A Google Gemini API key (free tier available)

## Installation

### 1. Install Python

**Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- Run the installer and **check "Add Python to PATH"**
- Verify installation by opening Command Prompt and typing: `python --version`

**Mac:**
- Install via Homebrew: `brew install python3`
- Or download from [python.org](https://www.python.org/downloads/)
- Verify installation in Terminal: `python3 --version`

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Install Required Packages

Open your terminal/command prompt in the bot's directory and run:

```bash
pip install praw google-generativeai
```

### 3. Create a Reddit Bot Account

1. **Create a new Reddit account** for your bot (e.g., "MySubredditBot")
2. **Create a Reddit application:**
   - Go to https://www.reddit.com/prefs/apps
   - Scroll down and click "create another app..."
   - Fill out the form:
     - **Name:** YourBotName
     - **App type:** Select "script"
     - **Description:** Brief description of what your bot does
     - **About URL:** Leave blank
     - **Redirect URI:** http://localhost:8080
   - Click "create app"
3. **Note your credentials:**
   - **client_id:** The string under "personal use script" (looks like `a1b2c3d4e5f6g7`)
   - **client_secret:** The "secret" value (longer string)

### 4. Get a Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 5. Set Up Environment Variables

**Windows (Command Prompt):**
```cmd
set REDDIT_CLIENT_ID=your_client_id_here
set REDDIT_CLIENT_SECRET=your_client_secret_here
set REDDIT_USERNAME=your_bot_username
set REDDIT_PASSWORD=your_bot_password
set GOOGLE_API_KEY=your_gemini_api_key
```

**Windows (PowerShell):**
```powershell
$env:REDDIT_CLIENT_ID="your_client_id_here"
$env:REDDIT_CLIENT_SECRET="your_client_secret_here"
$env:REDDIT_USERNAME="your_bot_username"
$env:REDDIT_PASSWORD="your_bot_password"
$env:GOOGLE_API_KEY="your_gemini_api_key"
```

**Mac/Linux:**
```bash
export REDDIT_CLIENT_ID="your_client_id_here"
export REDDIT_CLIENT_SECRET="your_client_secret_here"
export REDDIT_USERNAME="your_bot_username"
export REDDIT_PASSWORD="your_bot_password"
export GOOGLE_API_KEY="your_gemini_api_key"
```

**Permanent Setup (Mac/Linux):**

Add the export commands to your `~/.bashrc` or `~/.zshrc` file:
```bash
echo 'export REDDIT_CLIENT_ID="your_client_id_here"' >> ~/.bashrc
echo 'export REDDIT_CLIENT_SECRET="your_client_secret_here"' >> ~/.bashrc
echo 'export REDDIT_USERNAME="your_bot_username"' >> ~/.bashrc
echo 'export REDDIT_PASSWORD="your_bot_password"' >> ~/.bashrc
echo 'export GOOGLE_API_KEY="your_gemini_api_key"' >> ~/.bashrc
source ~/.bashrc
```

## Customizing for Your Subreddit

### Basic Configuration

Open `NoFlairBot.py` and modify these key variables:

1. **Update the user agent** (line 24):
   ```python
   user_agent="YourBotName by /u/YourRedditUsername"
   ```
   Replace with your bot's name and your personal Reddit username. This identifies your bot to Reddit's API.

2. **Change the subreddit** (line 30):
   ```python
   subreddit = reddit.subreddit("YourSubredditName")
   ```

3. **Change the bot username** (line 52):
   ```python
   bot_username = "YourBotUsername"
   ```

4. **Change the subreddit name** (line 53):
   ```python
   subreddit_name = "YourSubredditName"
   ```

### Customizing Bot Behavior

4. **Adjust the AI prompt** (lines 54-55):
   - Modify the `prompt_template` to change the bot's personality and tone
   - Example for a friendly approach:
   ```python
   prompt_template = """You are a helpful moderator. A user named "/u/{username}" posted without flair. 
   Politely remind them to add flair. Keep it friendly and brief (2 sentences)."""
   ```

5. **Rate limiting settings** (lines 45-47):
   ```python
   requests_per_thread = 3  # How many users to reply to per thread
   violation_limit_before_pinned_comment = 10  # Violations before pinned message
   requests_per_minute = 5  # API calls per minute
   requests_per_day = 250  # API calls per day
   ```

6. **Customize the pinned message** (lines 124-129):
   - Edit the `final_message` text to match your subreddit's tone

7. **Customize the disclaimer** (line 112):
   - Update the flair tutorial link to match your subreddit's guide

### Additional Tweaks

- **Change post age limit** (line 88): Currently set to 7 days
- **Adjust rate limits** based on your subreddit's activity level
- **Modify AI model**: Change `'models/gemini-2.5-flash'` to another Gemini model if needed

## Running the Bot

1. Open terminal/command prompt in the bot's directory
2. Run the bot:
   ```bash
   python NoFlairBot.py
   ```
3. The bot will run continuously and log activity to `log.txt`
4. Press `Ctrl+C` to stop the bot

## Troubleshooting

**Bot not responding:**
- Check that environment variables are set correctly
- Verify your Reddit bot account has permissions in the subreddit
- Check `log.txt` for error messages

**Rate limit errors:**
- Reduce `requests_per_minute` or `requests_per_day` values
- Check your Google Gemini API quota

**Authentication errors:**
- Double-check your Reddit credentials and API keys
- Ensure the bot account password is correct

## Important Notes

- Make sure your bot account is a moderator in your subreddit for full functionality (distinguishing comments, pinning)
- The bot saves its state in `bot_state.json` to avoid duplicate replies
- Monitor `log.txt` regularly to ensure the bot is working correctly
- Be respectful of Reddit's API terms of service and rate limits
- Test thoroughly in a private test subreddit before deploying

## Support

For issues with the bot, check the log file first. For Reddit API issues, consult the [PRAW documentation](https://praw.readthedocs.io/). For Gemini API issues, see [Google AI documentation](https://ai.google.dev/docs).
