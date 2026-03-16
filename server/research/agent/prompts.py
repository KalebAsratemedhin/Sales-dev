ANALYZE_WEBSITE_PROMPT = """You are analyzing a company website to identify pain points and use cases relevant to B2B sales.

Website URL: {url}

Website text content (excerpt):
---
{text}
---

{persona_block}

Ignore navigation, cookie banners, and legal text; focus on product descriptions and value propositions.

Provide a concise analysis. Use this exact structure:
- summary: 1-2 sentences about the company.
- pain_points: a list of 3-5 pain points (short phrases).
- use_cases: a list of 2-4 relevant use cases (short phrases).
Keep the total response concise (under 300 words)."""


def build_analyze_website_prompt_context(persona):
    if not persona or not any((persona.get("name"), persona.get("title_keywords"), persona.get("industry_keywords"))):
        return "Target persona: general B2B."
    parts = []
    if persona.get("name"):
        parts.append(f"Persona name: {persona['name']}.")
    if persona.get("title_keywords"):
        parts.append(f"Title keywords: {persona['title_keywords']}.")
    if persona.get("industry_keywords"):
        parts.append(f"Industry keywords: {persona['industry_keywords']}.")
    return "Target persona: " + " ".join(parts) if parts else "Target persona: general B2B."