"""
researcher.py — Agent 1
Uses the Tavily Search API to find current job market trends,
in-demand skills, and ATS keywords for a given job role.
"""

from tavily import TavilyClient


def research_job_role(job_role: str, tavily_api_key: str) -> dict:
    """
    Search the web for current hiring trends, must-have skills,
    and ATS keywords for `job_role`.

    Returns a dict with keys:
        - trends      : list of trend summaries
        - keywords    : list of ATS/recruiter keywords
        - skills      : list of in-demand skills
        - raw_results : list of raw Tavily result dicts
    """
    client = TavilyClient(api_key=tavily_api_key)

    queries = [
        f"{job_role} top skills recruiters look for 2025",
        f"{job_role} ATS keywords LinkedIn profile optimization",
        f"{job_role} job market trends hiring 2025",
    ]

    all_results = []
    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=3,
                include_answer=True,
            )
            all_results.append(
                {
                    "query": query,
                    "answer": response.get("answer", ""),
                    "results": response.get("results", []),
                }
            )
        except Exception as e:
            all_results.append({"query": query, "answer": "", "results": [], "error": str(e)})

    # Flatten useful text snippets for downstream agents
    snippets = []
    for item in all_results:
        if item.get("answer"):
            snippets.append(item["answer"])
        for r in item.get("results", []):
            if r.get("content"):
                snippets.append(r["content"][:400])

    combined_text = "\n\n".join(snippets)

    return {
        "job_role": job_role,
        "research_summary": combined_text[:6000],  # cap for LLM context
        "raw_results": all_results,
    }
