"""
rewriter.py — Agent 3
Uses Gemini to rewrite the LinkedIn headline, about section,
and skills list to be ATS-optimised and recruiter-friendly.
"""

from agents.llm import call_gemini_json

REWRITER_PROMPT = """
You are a world-class LinkedIn copywriter and ATS optimisation expert.

TARGET JOB ROLE: {job_role}

ORIGINAL PROFILE:
- Headline  : {headline}
- About     : {about}
- Skills    : {skills}
- Experience highlights: {experience}

ANALYSIS & GAPS:
{analysis_summary}

MARKET RESEARCH (keywords & trends):
{research_summary}

────────────────────────────────────────────
TASK
────────────────────────────────────────────
Rewrite this LinkedIn profile to maximise ATS score and recruiter appeal
for the target role. Be specific, achievement-oriented, and keyword-rich.

Return ONLY a valid JSON object — no prose, no markdown fences — with:

{{
  "headline"          : "<optimised headline ≤ 220 chars>",
  "about"             : "<optimised about section, 3-5 paragraphs, 300-2000 chars>",
  "skills"            : ["skill1", "skill2", ... up to 20 skills],
  "featured_keywords" : ["kw1", "kw2", ... top 10 ATS keywords embedded],
  "improvement_notes" : ["note1", "note2", "note3"]
}}
"""


def rewrite_profile(
    job_role: str,
    headline: str,
    about: str,
    skills: str,
    experience: str,
    analysis: dict,
    research: dict,
    gemini_api_key: str,
) -> dict:
    """
    Rewrite the LinkedIn profile sections for maximum ATS + recruiter impact.
    Returns a dict with optimised headline, about, skills, and keywords.
    """
    # Summarise the analysis for the prompt
    analysis_summary = (
        f"Overall score: {analysis.get('overall_score', '?')}/10\n"
        f"Missing keywords: {', '.join(analysis.get('missing_keywords', []))}\n"
        f"ATS gap: {analysis.get('ats_gap_analysis', '')}\n"
        f"Recommendations: {'; '.join(analysis.get('top_recommendations', []))}"
    )

    prompt = REWRITER_PROMPT.format(
        job_role=job_role,
        headline=headline or "(not provided)",
        about=about or "(not provided)",
        skills=skills or "(not provided)",
        experience=experience or "(not provided)",
        analysis_summary=analysis_summary,
        research_summary=research.get("research_summary", "No research available."),
    )

    try:
        result = call_gemini_json(prompt, gemini_api_key)
    except Exception as e:
        result = {
            "headline": headline,
            "about": about,
            "skills": skills.split(",") if skills else [],
            "featured_keywords": [],
            "improvement_notes": [f"Rewrite failed: {e}"],
        }

    return result
