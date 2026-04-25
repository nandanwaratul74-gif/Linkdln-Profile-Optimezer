"""
analyzer.py — Agent 2
Uses Gemini to score the user's current LinkedIn profile and
identify missing keywords / improvement areas.
"""

from agents.llm import call_gemini_json

ANALYZER_PROMPT = """
You are an expert LinkedIn profile coach and ATS specialist.

TARGET JOB ROLE: {job_role}

CURRENT PROFILE:
- Headline : {headline}
- About    : {about}
- Skills   : {skills}
- Experience highlights: {experience}

MARKET RESEARCH (current trends & keywords):
{research_summary}

────────────────────────────────────────────
TASK
────────────────────────────────────────────
Analyze the current profile against the job role and market research.
Return ONLY a valid JSON object — no prose, no markdown fences — with these exact keys:

{{
  "overall_score"        : <integer 1-10>,
  "headline_score"       : <integer 1-10>,
  "about_score"          : <integer 1-10>,
  "skills_score"         : <integer 1-10>,
  "missing_keywords"     : ["keyword1", "keyword2", ...],
  "present_keywords"     : ["keyword1", "keyword2", ...],
  "strengths"            : ["strength1", "strength2", ...],
  "weaknesses"           : ["weakness1", "weakness2", ...],
  "ats_gap_analysis"     : "<2-3 sentence summary of the biggest ATS gaps>",
  "top_recommendations"  : ["rec1", "rec2", "rec3", "rec4", "rec5"]
}}
"""


def analyze_profile(
    job_role: str,
    headline: str,
    about: str,
    skills: str,
    experience: str,
    research: dict,
    gemini_api_key: str,
) -> dict:
    """
    Score the user's current LinkedIn profile and identify gaps.
    Returns a structured analysis dict.
    """
    prompt = ANALYZER_PROMPT.format(
        job_role=job_role,
        headline=headline or "(not provided)",
        about=about or "(not provided)",
        skills=skills or "(not provided)",
        experience=experience or "(not provided)",
        research_summary=research.get("research_summary", "No research available."),
    )

    try:
        result = call_gemini_json(prompt, gemini_api_key)
    except Exception as e:
        # Graceful fallback so the pipeline doesn't crash
        result = {
            "overall_score": 5,
            "headline_score": 5,
            "about_score": 5,
            "skills_score": 5,
            "missing_keywords": [],
            "present_keywords": [],
            "strengths": [],
            "weaknesses": [f"Analysis failed: {e}"],
            "ats_gap_analysis": "Could not complete analysis.",
            "top_recommendations": [],
        }

    return result
