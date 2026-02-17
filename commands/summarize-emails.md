# /summarize-emails — Quick Email Summary

## Description
Get a fast, structured summary of your inbox without drafting responses.
Ideal for quick inbox checks throughout the day.

## Arguments
- `today` — Only emails from today (default)
- `unread` — Only unread emails
- `week` — Last 7 days
- `all` — All recent emails (last 30 days)

## Instructions

You are providing a quick email summary for {{YOUR_NAME}}. This is faster
and lighter than full triage — no response drafting, just awareness.

### Step 1: Get Current Time

Get the current date/time to determine what "today" and "recent" mean.

### Step 2: Scan Gmail

Query Gmail based on the argument provided:
- `today` — Emails from today only
- `unread` — Unread emails from the last 7 days
- `week` — All emails from the last 7 days
- `all` — All emails from the last 30 days

**Skip:**
- Automated notifications (unless from critical systems)
- Newsletters and marketing emails
- Emails where you're only CC'd (unless from key contacts)

### Step 3: Categorize

Group emails into categories:

**URGENT** — Needs immediate attention
- From key contacts (board, leadership, family)
- Explicit urgency signals ("urgent", "asap", "today")
- Someone is blocked waiting for your response
- Time-sensitive with deadline approaching

**IMPORTANT** — Needs attention soon
- From important relationships (team, customers, partners)
- Requires thoughtful response but not urgent
- Could impact active goals if delayed

**FYI** — Informational only
- Updates and status reports
- Project notifications
- Low-priority inquiries
- Can wait or be handled later

**WAITING ON YOU** — Threads where you were last contacted
- Unanswered questions directed at you
- Follow-ups where you haven't responded
- Conversations that need your input to continue

### Step 4: Present Summary

Format the output as:

```
EMAIL SUMMARY — [timeframe]
Scanned [N] emails

🔴 URGENT ([count])
• [Sender] — [Subject] ([time received])
  → [One-line summary of what they need]

🟡 IMPORTANT ([count])
• [Sender] — [Subject] ([time received])
  → [One-line summary]

⏳ WAITING ON YOU ([count])
• [Sender] — [Subject] ([days waiting])
  → [What they're waiting for]

📋 FYI ([count])
[Brief list of senders/subjects, or "Various updates and notifications"]

---

RECOMMENDATION:
[1-2 sentence action recommendation, e.g., "Focus on the 2 urgent items first, then respond to Sarah's proposal today."]
```

### Step 5: Offer Next Actions

After presenting the summary, offer:

```
Next steps:
• "Full triage" to get draft responses
• "Handle urgent" to draft just the urgent items
• "Mark as read" to clear FYI items
```

### Guidelines

- **Speed is critical** — this should take 30-60 seconds, not 5 minutes
- Use emojis for visual hierarchy (🔴 🟡 ⏳ 📋)
- One line per email — don't over-explain
- If inbox is empty or clear, celebrate: "✅ Inbox clear! No urgent items."
- Don't draft responses — this is awareness only
- Surface the most important insight at the top
- If there's a pattern (e.g., "5 customer emails about the same issue"), call it out

### Key Difference from /triage

| Feature | /summarize-emails | /triage |
|---------|-------------------|---------|
| Speed | 30-60 seconds | 2-3 minutes |
| Output | Summary only | Summaries + drafts |
| Use case | Quick check | Full inbox processing |
| Response drafting | No | Yes |
| Depth | Surface-level | Deep |
