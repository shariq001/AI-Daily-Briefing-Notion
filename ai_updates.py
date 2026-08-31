import os
import re
from datetime import datetime, timezone
import requests
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

client = genai.Client(api_key=GEMINI_API_KEY)

TOPICS = (
    "Artificial Intelligence, AI Agents, Agentic AI, Forward Deployed Engineer roles, "
    "AI companies like Anthropic and their product updates, and other major AI news"
)

PROMPT = f"""
Research today's genuine, verifiable news and updates on: {TOPICS}.

Rules:
- Use web search. Check multiple independent sources before stating any fact.
- Only include claims you found corroborated by at least one reputable source
  (official company blogs, established tech news outlets, primary announcements).
  If something is rumored or unconfirmed, either skip it or clearly label it as
  unconfirmed.
- Do not invent facts, dates, or figures. If you are not confident something is
  accurate, leave it out rather than guess.
- Focus on news from the last 24 hours. If there is no news in a category, skip it.
- We will only show new update for daily news, for 31 August 2026 we will show that days news, and for 30 August 2026 we will show that days news on 31 August 2026 post, and so on. 
- The post must be a summary of the news, not a full article. Keep it concise, clear, and professional. The readers will probably spend 2 - 3 minutes reading the post, so make it easy to skim and digest. 

Write the output as Markdown, structured like this:
# (a short, SEO-friendly title for today's AI news)

## (Section heading per topic cluster, e.g. "Anthropic & Claude Updates")
(short paragraph or bullet points on what happened, written clearly and
professionally, most preferably in bullet points. Include dates, names, and other relevant details. Use proper headings, subheadings, and bullet points to make the report easy to read. Don't go too much deep into technical details — the goal is to summarize the news for a general audience. don't go off-topic. If there is no news in a category, skip it. Keep short paragraphs and bullet points concise, clear, and professional. Avoid filler content. Don't go for more than 2 paragraphs per section.)

... repeat sections for each topic area that had real news today ...

## References
- (Source name) — (full URL)
- (Source name) — (full URL)
(list every distinct source actually used, with the full URL, in a bulleted list. If you used multiple articles from the same source, list each article separately. and mention for which topic is that url points to. If you used a source for multiple topics, list it once per topic.)

Keep the tone professional, clear, and well-organized. Do not pad with filler
if there isn't real news in a category — a shorter, accurate report is better
than a padded one.
"""

def get_report():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=PROMPT,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )
    return response.text


def markdown_to_notion_blocks(markdown_text):
    """Small, deliberately simple converter: headings, bullets, paragraphs only.
    No images, no nested lists, no tables — good enough for a daily text report."""
    blocks = []
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("### "):
            block_type, text = "heading_3", line[4:]
        elif line.startswith("## "):
            block_type, text = "heading_2", line[3:]
        elif line.startswith("# "):
            block_type, text = "heading_1", line[2:]
        elif line.startswith("- ") or line.startswith("* "):
            block_type, text = "bulleted_list_item", line[2:]
        else:
            block_type, text = "paragraph", line

        text = text[:2000]  # Notion's per-block rich_text limit

        blocks.append({
            "object": "block",
            "type": block_type,
            block_type: {"rich_text": [{"type": "text", "text": {"content": text}}]},
        })

    # Signature line, always last
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Muhammad Shariq's AI Employee Research"},
                "annotations": {"italic": True},
            }]
        },
    })
    return blocks[:100]  # Notion caps children at 100 blocks per request


def post_to_notion(title, blocks):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {  # <-- change "Name" if your database's title property is called something else
                "title": [{"text": {"content": title}}]
            }
        },
        "children": blocks,
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    title = f"{today}: AI Updates"

    print(f"Researching report for: {title}")
    report_markdown = get_report()

    print("Converting to Notion blocks...")
    blocks = markdown_to_notion_blocks(report_markdown)

    print("Posting to Notion...")
    result = post_to_notion(title, blocks)

    print("Done. Notion page URL:", result.get("url", "unknown"))


if __name__ == "__main__":
    main()