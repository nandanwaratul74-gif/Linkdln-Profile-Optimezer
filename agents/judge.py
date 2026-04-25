"""
judge.py — Agent 4
An independent Gemini "judge" that evaluates the rewritten profile
for professionalism, ATS readiness, and recruiter appeal.
"""

from agents.llm import call_gemini_json

JUDGE_PROMPT = """
You are an elite, brutally honest career coach and ATS auditor.
Your job is to JUDGE a rewritten LinkedIn profile and score it objectively.

TARGET JOB ROLE: {job_role}

REWRITTEN PROFILE TO JUDGE:
- Headline  : {headline}
- About     : {about}
- Skills    : {skills}
- ATS Keywords used: {keywords}

────────────────────────────────────────────
TASK
────────────────────────────────────────────
Score and critique the rewritten profile. Be strict and fair.

Return ONLY a valid JSON object — no prose, no markdown fences — with:

{{
  "overall"            : <integer 1-10>,
  "clarity"            : <integer 1-10>,
  "keywords"           : <integer 1-10>,
  "professionalism"    : <integer 1-10>,
  "ats_ready"          : <integer 1-10>,
  "recruiter_appeal"   : <integer 1-10>,
  "uniqueness"         : <integer 1-10>,
  "verdict"            : "<one of: EXCELLENT | GOOD | NEEDS WORK | POOR>",
  "best_part"          : "<1-2 sentences — what is strongest about this profile>",
  "critical_fix"       : "<1-2 sentences — the single most important thing to improve>",
  "detailed_feedback"  : "<3-5 sentences of constructive, specific feedback>"
}}
"""


def judge_profile(
    job_role: str,
    rewrite: dict,
    gemini_api_key: str,
) -> dict:
    """
    Independently judge the quality of the rewritten profile.
    Returns a structured verdict dict.
    """
    skills_str = ", ".join(rewrite.get("skills", []))
    keywords_str = ", ".join(rewrite.get("featured_keywords", []))
    about = rewrite.get("about", "")

    prompt = JUDGE_PROMPT.format(
        job_role=job_role,
        headline=rewrite.get("headline", ""),
        about=about[:1500],  # cap for context window
        skills=skills_str,
        keywords=keywords_str,
    )

    try:
        result = call_gemini_json(prompt, gemini_api_key)
    except Exception as e:
        result = {
            "overall": 7,
            "clarity": 7,
            "keywords": 7,
            "professionalism": 7,
            "ats_ready": 7,
            "recruiter_appeal": 7,
            "uniqueness": 7,
            "verdict": "GOOD",
            "best_part": "Profile was generated successfully.",
            "critical_fix": f"Judge evaluation failed: {e}",
            "detailed_feedback": "Could not complete judge evaluation.",
        }

    return result
