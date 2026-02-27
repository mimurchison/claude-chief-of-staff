# MCP Server Setup

MCP (Model Context Protocol) servers give Claude access to external services
like Gmail, Google Calendar, Slack, and more. The more servers you connect,
the more powerful your AI Chief of Staff becomes.

---

## Required Servers

These two servers are the minimum for a useful experience.

### Gmail

Enables: Email triage, drafting, sending, searching

**Installation:**

```bash
# Using the Gmail MCP server
npx @anthropic-ai/claude-code mcp add gmail
```

Follow the OAuth flow to authorize access to your Gmail account.

**Configuration:**

The Gmail MCP server is configured in your Claude Code MCP settings. The exact
location depends on your installation, but is typically at:

```
~/.claude/mcp_settings.json
```

**Multiple accounts:**

If you have separate work and personal Gmail accounts, you can add them as
separate MCP servers:

```bash
npx @anthropic-ai/claude-code mcp add gmail         # Work account
npx @anthropic-ai/claude-code mcp add gmail-personal # Personal account
```

Update your CLAUDE.md to reference both servers:
```markdown
| Gmail (work) | Connected | Work email triage |
| Gmail (personal) | Connected | Personal email triage |
```

**Verify it works:**

```
> Search my email for messages from today
```

---

### Google Calendar

Enables: Scheduling, availability checks, meeting prep, calendar creation

**Installation:**

```bash
npx @anthropic-ai/claude-code mcp add google-calendar
```

Follow the OAuth flow to authorize calendar access.

**Verify it works:**

```
> What's on my calendar today?
> Am I free next Tuesday at 2pm?
```

---

## Recommended Servers

These significantly enhance the experience but aren't strictly required.

### Slack

Enables: Slack DM triage, channel monitoring, message drafting

**Installation:**

```bash
npx @anthropic-ai/claude-code mcp add slack
```

You'll need a Slack app token with appropriate scopes (channels:history,
im:history, search:read, chat:write, users:read).

**Verify it works:**

```
> Show me my recent Slack DMs
> Search Slack for messages about "product launch"
```

---

## Optional Servers

Add these based on your workflow.

### WhatsApp

Enables: WhatsApp message triage, contact search, messaging

**Note:** WhatsApp MCP requires a bridge service. Setup varies by implementation.

```bash
npx @anthropic-ai/claude-code mcp add whatsapp
```

**Verify it works:**

```
> Show my recent WhatsApp messages
```

---

### iMessage (macOS Only)

Enables: iMessage triage, reading messages

**Note:** Only works on macOS. Requires accessibility permissions.

```bash
npx @anthropic-ai/claude-code mcp add imessage
```

**Verify it works:**

```
> Show my recent iMessages
```

---

### Sybill

Enables: AI meeting summaries, transcripts, action items, participant insights, sentiment analysis

Sybill uses a custom MCP server built at Quandri. It has two components:
1. A **webhook receiver** that stores Sybill meeting data locally via Svix webhooks
2. An **MCP server** that exposes query tools over the stored data

**Installation:**

```bash
# 1. Build the server (one time)
cd /Users/abhiprajapati/Documents/work/quandri/sybill-mcp
npm install && npm run build

# 2. Add the MCP server to Claude Code
claude mcp add sybill -- node /Users/abhiprajapati/Documents/work/quandri/sybill-mcp/dist/index.js serve

# 3. Set webhook secret and start the webhook listener (run as background service)
export SYBILL_WEBHOOK_SECRET=whsec_...  # Get from Sybill dashboard
node /Users/abhiprajapati/Documents/work/quandri/sybill-mcp/dist/index.js webhook
```

**Environment variables:**
- `SYBILL_WEBHOOK_SECRET` — Svix secret from Sybill dashboard (required for webhook)
- `SYBILL_DB_PATH` — SQLite path (default: `~/.sybill-mcp/data.db`)
- `SYBILL_WEBHOOK_PORT` — Webhook port (default: 3456)

**Available tools:**
- `list_meetings` — List recent meetings (filter by date, participant)
- `get_meeting` — Full meeting details (summary, transcript, action items, sentiment)
- `search_meetings` — Full-text search across meetings
- `get_action_items` — Action items across meetings (filter by assignee)
- `get_participant_insights` — Aggregated insights for a person across meetings

**Verify it works:**

```
> List my recent meeting summaries from Sybill
> Search meetings for "product roadmap"
> Show action items assigned to me
```

---

### Granola

Enables: Meeting notes search and retrieval

Granola records and summarizes your meetings. The MCP server lets Claude
search and retrieve those notes.

```bash
npx @anthropic-ai/claude-code mcp add granola
```

**Verify it works:**

```
> Search my meeting notes for "product roadmap"
```

---

### PostHog

Enables: Product analytics queries, dashboard access

Useful for product leaders who want Claude to pull metrics during conversations.

```bash
npx @anthropic-ai/claude-code mcp add posthog
```

**Verify it works:**

```
> What's our weekly active users trend?
```

---

### Linear

Enables: Issue tracking, project management, engineering workflow

Useful for engineering leaders managing sprints and backlogs.

```bash
npx @anthropic-ai/claude-code mcp add linear
```

**Verify it works:**

```
> Show my assigned Linear issues
```

---

## Adding Custom MCP Servers

Claude Code supports any MCP-compatible server. If you use a service that has
an MCP server available, you can add it:

```bash
# Generic pattern
npx @anthropic-ai/claude-code mcp add <server-name>

# Or configure manually in mcp_settings.json
```

After adding a server, update your CLAUDE.md's "MCP Servers" section so Claude
knows it's available.

---

## Troubleshooting

### "MCP server not found"

Make sure the server is installed:
```bash
npx @anthropic-ai/claude-code mcp list
```

### "Authentication failed"

Re-authenticate:
```bash
npx @anthropic-ai/claude-code mcp remove gmail
npx @anthropic-ai/claude-code mcp add gmail
```

### "Rate limited"

MCP servers may rate-limit requests. If you see rate limit errors:
- Reduce automation frequency in `schedules.yaml`
- Use `quick` mode for triage instead of full scans
- Batch queries when possible

### Server-specific issues

Each MCP server may have its own setup requirements (API keys, OAuth scopes,
permissions). Check the server's documentation for specific troubleshooting.

---

## What to Connect First

If you're just getting started, connect servers in this order:

1. **Gmail** — Unlocks email triage (biggest productivity win)
2. **Google Calendar** — Unlocks scheduling intelligence
3. **Slack** — Unlocks Slack triage (if your team uses Slack)
4. **Everything else** — Add as needed based on your workflow

You can always add more servers later. The system degrades gracefully —
if a server isn't connected, Claude simply skips that channel during triage.
