# AI Daily Briefing → Notion

An autonomous loop that researches daily AI industry news and publishes a
formatted, sourced summary to Notion — every night, with no laptop required.

## What it does

Every day at **10:00 PM PST** (6:00 AM UTC), this job:

1. Uses Gemini's web search (grounding) to research the day's genuine news on
   AI, AI Agents, Agentic AI, Forward Deployed Engineering, and major AI
   company updates (Anthropic and others).
2. Cross-checks claims across multiple sources before including them —
   unconfirmed or single-source claims are labeled or dropped.
3. Writes a clean, SEO-structured Markdown report with headings and a
   References section.
4. Publishes it as a new page in a Notion database, titled
   `Month Day, Year: AI Updates`.

Runs entirely on GitHub's infrastructure via GitHub Actions — no local
machine needs to be on.

## Architecture