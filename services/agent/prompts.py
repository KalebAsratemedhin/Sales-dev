ANALYZE_WEBSITE_PROMPT = """You are analyzing a company website to identify pain points and use cases relevant to B2B sales.

Website URL: {url}

Website text content (excerpt):
---
{text}
---

Provide a concise analysis. Use this exact structure:
- summary: 1-2 sentences about the company.
- pain_points: a list of 3-5 pain points (short phrases).
- use_cases: a list of 2-4 relevant use cases (short phrases).
Keep the total response concise (under 300 words)."""