import requests

BASE = "https://api.ziprecruiter.com/jobs/v1"

def fetch_ziprecruiter(cfg):
    """
    cfg keys:
      api_key (required)
      query, location (strings)
      radius_miles (int)
      days_age (int)
      per_page (int)
      page (int)
    """
    key = cfg.get("api_key")
    if not key:
        return []

    params = {
        "api_key": key,
        "search": cfg.get("query", ""),
        "location": cfg.get("location", ""),
        "radius_miles": int(cfg.get("radius_miles", 50)),
        "days_age": int(cfg.get("days_age", 14)),
        "page": int(cfg.get("page", 1)),
        "jobs_per_page": int(cfg.get("per_page", 25)),
    }

    try:
        r = requests.get(BASE, params=params, timeout=30)
        r.raise_for_status()
    except Exception:
        return []

    data = r.json()
    out = []
    for j in data.get("jobs", []):
        company = (j.get("hiring_company") or {}).get("name")
        city = j.get("city")
        state = j.get("state")
        loc = ", ".join([p for p in [city, state] if p])
        out.append({
            "id": j.get("id"),
            "title": j.get("name"),
            "company": company,
            "location": loc or j.get("location"),
            "url": j.get("url"),
            "posted_at": j.get("posted_time") or j.get("posted_time_friendly"),
            "salary": j.get("salary_min") or j.get("salary_max"),
        })
    return out
