import requests

BASE = "https://api.ziprecruiter.com/jobs/v1"

def fetch_ziprecruiter(cfg):
    """
    cfg keys expected:
      api_key (required)
      query, location (strings)
      radius_miles (int)
    """
    key = cfg.get("api_key")
    if not key:
        return []

    params = {
        "api_key": key,
        "search": cfg.get("query", ""),
        "location": cfg.get("location", ""),
        "radius_miles": cfg.get("radius_miles", 25),
        "days_ago": cfg.get("days_ago", 14),
        "jobs_per_page": cfg.get("per_page", 20),
    }

    try:
        r = requests.get(BASE, params=params, timeout=30)
        r.raise_for_status()
    except Exception:
        return []

    data = r.json()
    out = []
    for j in data.get("jobs", []):
        company = j.get("hiring_company", {}).get("name")
        city = j.get("city")
        state = j.get("state")
        loc = ", ".join(p for p in [city, state] if p)

        out.append({
            "id": j.get("id"),
            "title": j.get("name"),
            "company": company,
            "location": loc,
            "url": j.get("url"),
            "posted_at": j.get("posted_time_friendly"),
            "salary": j.get("salary_min") or j.get("salary_max"),
        })
    return out
