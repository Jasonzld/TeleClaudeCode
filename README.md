# TeleClaudeCode

Telegram bot powered by **Claude Code CLI** (`claude -p`).

## Quick Start (Polling Mode)

```bash
# 1. Clone & install
git clone https://github.com/Jasonzld/TeleClaudeCode.git
cd TeleClaudeCode
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env: set TELEGRAM_BOT_TOKEN

# 3. Run
python launcher.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Bot token from @BotFather |
| `CLAUDE_BIN` | `claude` | Path to Claude Code CLI |
| `CLAUDE_TIMEOUT_SEC` | `120` | Execution timeout |
| `CLAUDE_MODEL` | _(default)_ | Model override (e.g. `sonnet`, `opus`) |
| `CLAUDE_PERMISSION_MODE` | _(default)_ | Permission mode (e.g. `bypassPermissions`) |
| `CLAUDE_MAX_BUDGET_USD` | _(none)_ | Max spend per request |
| `DIRECT_CHAT` | `true` | Allow direct messages without `/ask` prefix |
| `MODE` | `polling` | `polling` (local) or `webhook` (production) |

## Architecture

```
User → Telegram → polling.py → claude -p "prompt" → stdout → Telegram → User
```

## License

MIT
