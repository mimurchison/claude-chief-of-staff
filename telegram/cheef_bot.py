#!/usr/bin/env python3
"""
Cheef Telegram Bot
Bridges Telegram to Claude Code CLI running locally on Mac.

Setup:
1. Create ~/.claude/telegram/.env with TELEGRAM_BOT_TOKEN and ALLOWED_TELEGRAM_USER_ID
2. pip3 install "python-telegram-bot[job-queue]>=20.0" python-dotenv
3. Run manually first to test: python3 cheef_bot.py
4. Then install as launchd service for persistence
"""

import asyncio
import json
import logging
import os
import subprocess
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv(Path.home() / ".claude" / "telegram" / ".env")

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_TELEGRAM_USER_ID"])
PROJECT_DIR = os.environ.get(
    "CHEEF_PROJECT_DIR",
    str(Path.home() / "claude-chief-of-staff")
)
CLAUDE_BIN = os.environ.get(
    "CLAUDE_BIN",
    subprocess.run(["which", "claude"], capture_output=True, text=True).stdout.strip()
    or "/opt/homebrew/bin/claude"
)
MAX_HISTORY_TURNS = 10                   # rolling window of message pairs
TELEGRAM_MAX_CHARS = 4000               # slightly under 4096 for safety
CLAUDE_TIMEOUT = 180.0                  # seconds — MCP calls can be slow

LOG_FILE = str(Path.home() / ".claude" / "telegram" / "cheef_bot.log")

logging.basicConfig(
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),        # also print to stdout for manual testing
    ]
)
logger = logging.getLogger(__name__)

# ── Conversation History ───────────────────────────────────────────────────────
# In-memory rolling history per chat_id.
# Claude CLI -p mode is stateless per invocation, so we inject context manually.
conversation_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=MAX_HISTORY_TURNS * 2))


def build_prompt_with_history(chat_id: int, new_message: str) -> str:
    """Prepend recent conversation turns to the new message for context continuity."""
    history = list(conversation_history[chat_id])
    if not history:
        return new_message

    lines = []
    for entry in history:
        prefix = "Human" if entry["role"] == "user" else "Assistant"
        content = entry["content"]
        # Truncate old turns to avoid excessive token usage
        if len(content) > 600:
            content = content[:600] + "... [truncated]"
        lines.append(f"[{prefix}]: {content}")

    context = "\n".join(lines)
    return (
        f"[Previous conversation context — use this to maintain continuity]\n"
        f"{context}\n\n"
        f"[Current message from user]\n"
        f"{new_message}"
    )


# ── Claude Invocation ─────────────────────────────────────────────────────────

async def invoke_claude(prompt: str) -> str:
    """
    Run `claude -p <prompt> --output-format json` as an async subprocess.
    Returns the text response, or an error string.
    """
    cmd = [
        CLAUDE_BIN,
        "-p", prompt,
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--model", "sonnet",
    ]

    logger.info(f"Invoking Claude. Prompt length: {len(prompt)} chars")

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=PROJECT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HOME": str(Path.home())},
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=CLAUDE_TIMEOUT,
        )

        if process.returncode != 0:
            err = stderr.decode().strip()
            logger.error(f"Claude CLI exited with code {process.returncode}: {err[:500]}")
            return f"Cheef hit an error (exit {process.returncode}). Check logs at {LOG_FILE}"

        raw = stdout.decode().strip()
        try:
            output = json.loads(raw)
            result = output.get("result", "")
            if not result:
                logger.warning(f"Empty result in Claude output: {raw[:300]}")
                return "Got an empty response from Cheef. Try again."
            logger.info(f"Claude response length: {len(result)} chars")
            return result
        except json.JSONDecodeError:
            # Fallback: return raw output if JSON parsing fails
            logger.warning(f"JSON parse failed, returning raw output. First 200 chars: {raw[:200]}")
            return raw if raw else "No response returned."

    except asyncio.TimeoutError:
        logger.error(f"Claude timed out after {CLAUDE_TIMEOUT}s")
        return (
            f"That took too long (>{int(CLAUDE_TIMEOUT)}s). "
            "MCP servers may be slow or unresponsive. Try again or use a simpler request."
        )
    except FileNotFoundError:
        logger.error(f"Claude binary not found at: {CLAUDE_BIN}")
        return f"Claude CLI not found at `{CLAUDE_BIN}`. Check that Claude Code is installed."
    except Exception as e:
        logger.error(f"Unexpected error invoking Claude: {e}", exc_info=True)
        return f"Something went wrong: {type(e).__name__}: {str(e)}"


# ── Message Chunking ──────────────────────────────────────────────────────────

def chunk_message(text: str, max_len: int = TELEGRAM_MAX_CHARS) -> list[str]:
    """
    Split long responses into Telegram-safe chunks.
    Splits on paragraph breaks when possible to preserve readability.
    """
    if len(text) <= max_len:
        return [text]

    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= max_len:
            chunks.append(remaining)
            break
        # Prefer splitting on double newline (paragraph break)
        split_at = remaining.rfind("\n\n", 0, max_len)
        if split_at == -1:
            # Fall back to single newline
            split_at = remaining.rfind("\n", 0, max_len)
        if split_at == -1:
            # Hard split at max_len
            split_at = max_len
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip("\n")

    return chunks


# ── Auth ─────────────────────────────────────────────────────────────────────

def is_authorized(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else None
    return uid == ALLOWED_USER_ID


# ── Handlers ──────────────────────────────────────────────────────────────────

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return  # silent reject
    await update.message.reply_text(
        "Cheef is online.\n\n"
        "Ask anything, or use:\n"
        "• /gm — morning briefing\n"
        "• /triage — inbox scan\n"
        "• /my_tasks — task list\n"
        "• /clear — reset conversation context"
    )


async def handle_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    chat_id = update.effective_chat.id
    conversation_history[chat_id].clear()
    await update.message.reply_text("Context cleared. Fresh start.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        logger.warning(
            f"Unauthorized message from user_id={update.effective_user.id if update.effective_user else 'unknown'}"
        )
        return  # silent reject — don't reveal the bot exists to strangers

    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Show typing indicator while Claude processes
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Build prompt with rolling conversation context
    prompt = build_prompt_with_history(chat_id, user_message)

    # Store user message before invoking Claude
    conversation_history[chat_id].append({"role": "user", "content": user_message})

    # Invoke Claude (async, non-blocking)
    response_text = await invoke_claude(prompt)

    # Store Claude's response
    conversation_history[chat_id].append({"role": "assistant", "content": response_text})

    # Send response, chunking if needed
    chunks = chunk_message(response_text)
    for i, chunk in enumerate(chunks):
        if i > 0:
            await asyncio.sleep(0.3)  # brief pause between chunks
        await update.message.reply_text(chunk)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info(f"Starting Cheef Telegram Bot (allowed_user_id={ALLOWED_USER_ID})")
    logger.info(f"Claude binary: {CLAUDE_BIN}")
    logger.info(f"Project dir: {PROJECT_DIR}")

    app = Application.builder().token(BOT_TOKEN).build()

    # Explicit command handlers
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("clear", handle_clear))

    # Route all other text messages AND commands (like /gm, /triage, /my_tasks)
    # through handle_message so Claude can invoke the skill
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))  # catches /gm, /triage, etc.

    app.run_polling(
        poll_interval=1.0,          # check for new messages every 1 second
        timeout=30,                 # long-polling timeout
        drop_pending_updates=True,  # skip messages sent while bot was offline
    )


if __name__ == "__main__":
    main()
