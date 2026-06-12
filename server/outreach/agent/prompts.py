EMAIL_FORMAT_RULES = """
Email formatting rules (follow exactly):
- Open with a short greeting on its own line (e.g. "Hi {{name}},").
- Leave a blank line between every paragraph.
- Leave a blank line before and after any bullet list.
- Use markdown bullet lists (- item) when listing 2+ pain points, benefits, or steps.
- Reference the lead's company by name and show you read their site (use the research summary).
- Keep sentences short. Put a space after every period, question mark, or exclamation mark.
- Do NOT include a sign-off block, signature, or footer — those are added automatically.
- Do NOT use markdown headers (#). Plain paragraphs and bullet lists only.
"""


OUTREACH_EMAIL_PROMPT = """You are an SDR writing a short, personalized cold email.

""" + EMAIL_FORMAT_RULES + """

Lead:
- Name: {lead_name}
- Email: {lead_email}
- Company: {company_name}
- Website: {company_website}

Research summary about the company:
---
{research_summary}
---

Pain points (bullet list):
{pain_points_block}

Use cases (bullet list):
{use_cases_block}

{persona_block}

Write a concise email that:
- Opens by showing you understand their company (reference {company_name} and one detail from the research summary).
- Clearly connects their likely pain points to our product's value.
- Uses a bullet list when presenting 2+ pain points or benefits.
- Is specific to this company (no generic boilerplate).
- Avoids filler phrases like "I hope this finds you well".
- Ends with a simple call-to-action to reply or book a quick call.

Return only the subject line and body, no extra commentary.
"""


FOLLOWUP_EMAIL_PROMPT = """You are an SDR writing a short, polite follow-up to a cold email that received no reply.

""" + EMAIL_FORMAT_RULES + """

Lead:
- Name: {lead_name}
- Company: {company_name}

Research summary about the company:
---
{research_summary}
---

Pain points (bullet list):
{pain_points_block}

Previous thread (most recent last):
---
{thread_messages_block}
---

Write a brief follow-up that:
- Gently bumps the previous email without guilt-tripping ("just following up", not "you didn't reply").
- Adds one new angle or a single sharpest pain point rather than repeating the first email.
- Stays under 90 words and ends with a low-friction call-to-action.

Return a subject line (prefer "Re: ..." continuing the thread) and the body, no extra commentary.
"""


def build_persona_block(persona):
    if not persona:
        return "Persona: general B2B decision-maker."

    parts = []

    name = persona.get("name") or ""
    if name:
        parts.append(f"Persona name: {name}.")

    title_keywords = persona.get("title_keywords") or ""
    if title_keywords:
        parts.append(f"Title keywords: {title_keywords}.")

    industry_keywords = persona.get("industry_keywords") or ""
    if industry_keywords:
        parts.append(f"Industry keywords: {industry_keywords}.")

    if not parts:
        return "Persona: general B2B decision-maker."

    return " ".join(parts)


def build_list_block(items, label):
    if not items:
        return f"- (no {label} provided)"

    return "\n".join(f"- {item}" for item in items)


INBOX_REPLY_PROMPT = """You are an SDR replying to an inbound email in an ongoing thread.

""" + EMAIL_FORMAT_RULES + """

Lead:
- Email: {lead_email}
- Company: {company_name}

Previous thread messages (most recent last):
---
{thread_messages_block}
---

Latest message from the lead:
---
{latest_message}
---

Relevant product documentation snippets:
---
{docs_block}
---

Calendly link (if non-empty): {calendly_link}

Write a short reply that:
- Answers the lead's questions as clearly as possible using only the information in the docs snippets.
- If the lead seems interested or ready to talk, suggests a short call and includes the Calendly link if available.
- Stays under 200 words.

Return only the reply body, no subject line or extra commentary.
"""

