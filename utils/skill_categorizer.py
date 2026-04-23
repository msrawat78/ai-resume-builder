"""
skill_categorizer.py — Groups raw skill strings into human-readable category labels.

Used by all three templates to display skills as category pills
(e.g. "AI & LLM", "Cloud & Infrastructure") rather than individual tool names.
Falls back to the raw skill list if no categories match.
"""

from __future__ import annotations

# Each category maps to a set of keyword fragments (case-insensitive match)
CATEGORY_MAP: dict[str, list[str]] = {
    "Leadership & Strategy": [
        "cdo","fractional","analytics vertical","team building","p&l","agile","scrum",
        "solution architect","pre-sales","presales","client management","strategic",
        "operational excellence","governance","portfolio","stakeholder","roadmap",
        "effort estimation","proposal","commercial","pre sales",
    ],
    "AI & LLM": [
        "llm","gpt","chatgpt","claude","prompt","langchain","openai","anthropic",
        "orchestration","chain of thought","tokenization","responsible ai",
        "data ethics","generative","rag","vector","embedding","fine-tun",
    ],
    "Cloud & Infrastructure": [
        "aws","azure","gcp","ec2","route 53","load balancer","cloud","adf",
        "pipeline","medallion","data factory","databricks","spark","etl","elt",
        "api integration","devops","ci/cd","infrastructure",
    ],
    "Data Engineering": [
        "mysql","postgresql","sql","database","etl","elt","warehouse","lakehouse",
        "schema","aggregation","pipeline","airflow","dbt","kafka","mongodb",
        "redis","snowflake","bigquery","redshift",
    ],
    "BI & Visualisation": [
        "power bi","sap analytics","tableau","spotfire","looker","qlik","metabase",
        "dashboard","kpi","mis","reporting","bi","visuali","pbir",
    ],
    "ML & Analytics": [
        "scikit","sklearn","regression","classification","neural","time series",
        "statistical","machine learning","deep learning","nlp","forecasting",
        "clustering","xgboost","tensorflow","pytorch","model","ml",
    ],
    "Programming": [
        "python","r ","r,","vba","macro","excel","sql","javascript","typescript",
        "java","scala","golang","bash","shell","github","git","notebook",
    ],
    "Governance & Compliance": [
        "responsible ai","data ethics","compliance","gdpr","hipaa","six sigma",
        "iso","audit","risk","policy","framework","regulatory",
    ],
}


def categorize(skills: list[str]) -> list[str]:
    """
    Given a flat list of skill strings, return a deduplicated ordered list
    of category labels that best represent the skills.

    If fewer than 2 categories match, returns the original list unchanged
    (so short, already-categorised skill lists pass through).
    """
    if not skills:
        return []

    found: list[str] = []
    for cat, keywords in CATEGORY_MAP.items():
        for skill in skills:
            sl = skill.lower()
            if any(kw in sl for kw in keywords):
                if cat not in found:
                    found.append(cat)
                break  # one skill match is enough to include the category

    # If very few categories matched, return raw skills as pills instead
    if len(found) < 2:
        return skills

    return found
