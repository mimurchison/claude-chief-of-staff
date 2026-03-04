# Telegram Bot Setup

The Telegram bot gives you mobile access to your AI Chief of Staff. Send a message from your phone and get a response powered by Claude Code — with all your MCP servers, context, and commands available.

---

## Prerequisites

- Claude Code CLI installed and working locally (`claude --version`)
- Telegram account
- macOS (the background service uses launchd; the bot itself runs on any Unix)

---

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts — choose a name and username for your bot
4. BotFather gives you a **bot token** (looks like `7123456789:AAF...`)
5. Save this token

---

## Step 2: Get Your Telegram User ID

You must whitelist your own Telegram user ID so only you can use the bot.

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. It replies with your numeric user ID (e.g., `123456789`)
4. Save this number

---

## Step 3: Install

If you haven't run the installer yet:

```bash
./install.sh
```

When prompted "Set up Telegram bot?", type `y`. The installer will copy bot files to `~/.claude/telegram/`, install Python dependencies, and optionally install a launchd service.

**If you already ran the installer without Telegram**, set it up manually:

```bash
mkdir -p ~/.claude/telegram
cp telegram/cheef_bot.py ~/.claude/telegram/
cp telegram/requirements.txt ~/.claude/telegram/
cp telegram/.env.example ~/.claude/telegram/.env.example
pip3 install -r ~/.claude/telegram/requirements.txt
```

---

## Step 4: Configure Credentials

```bash
cp ~/.claude/telegram/.env.example ~/.claude/telegram/.env
```

Edit `~/.claude/telegram/.env`:

```bash
TELEGRAM_BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALLOWED_TELEGRAM_USER_ID=123456789
CHEEF_PROJECT_DIR=/Users/yourname/claude-chief-of-staff
CLAUDE_BIN=/opt/homebrew/bin/claude
```

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | From BotFather (Step 1) |
| `ALLOWED_TELEGRAM_USER_ID` | Your Telegram user ID (Step 2) |
| `CHEEF_PROJECT_DIR` | Path to your cloned `claude-chief-of-staff` folder |
| `CLAUDE_BIN` | Path to Claude binary — find it with `which claude` |

---

## Step 5: Test Manually First

```bash
python3 ~/.claude/telegram/cheef_bot.py
```

Open Telegram, find your bot by username, and send `/start`. You should see the welcome message. Send any message — it should route through Claude and reply.

Press `Ctrl+C` to stop.

---

## Step 6: Install as a Background Service (macOS)

To run the bot automatically and keep it running after restarts:

```bash
# Substitute your home directory into the template
sed "s|{{HOME_DIR}}|$HOME|g" \
    telegram/com.cheef.telegram.plist.template \
    > ~/Library/LaunchAgents/com.cheef.telegram.plist

# Load the service
launchctl load ~/Library/LaunchAgents/com.cheef.telegram.plist
```

The bot will now start automatically when you log in.

---

## Managing the Service

```bash
# Stop the bot
launchctl unload ~/Library/LaunchAgents/com.cheef.telegram.plist

# Start the bot
launchctl load ~/Library/LaunchAgents/com.cheef.telegram.plist

# Check if it's running
launchctl list | grep cheef

# View logs
tail -f ~/.claude/telegram/cheef_bot.log
tail -f ~/.claude/telegram/cheef_bot_error.log
```

---

## Available Commands

| Command | What it does |
|---------|-------------|
| `/start` | Show welcome message |
| `/clear` | Reset conversation context |
| `/gm` | Morning briefing |
| `/triage` | Inbox triage |
| `/my_tasks` | Task list |
| Any message | Routes to Claude — ask anything |

---

## Troubleshooting

**Bot doesn't respond**
1. Check it's running: `launchctl list | grep cheef`
2. Check logs: `tail -50 ~/.claude/telegram/cheef_bot_error.log`
3. Verify token and user ID in `~/.claude/telegram/.env`

**"Claude CLI not found" error**
Set `CLAUDE_BIN` in your `.env` to the absolute path. Find it with: `which claude`

**Responses time out**
Claude can take up to 3 minutes when MCP servers are slow. If consistently timing out, try a simpler request or verify MCP servers are working in a regular Claude Code session.

**Bot works manually but not as a service**
The launchd service needs an absolute `CLAUDE_BIN` path. Verify it in your `.env` and confirm the binary exists at that location.

---

## Security Notes

- Your `.env` file contains sensitive credentials — it is gitignored by default
- Never commit your `.env` file
- The bot silently rejects all users except your whitelisted user ID
- All Claude invocations run with your local permissions and full MCP access
