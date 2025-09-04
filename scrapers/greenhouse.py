import requests

def fetch_greenhouse(company_shortname):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_shortname}/jobs"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except Exception:
        return []
    data = r.json()
    out = []
    for j in data.get("jobs", []):
        loc = j.get("location", {}).get("name")
        out.append({
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company", {}).get("name") or company_shortname,
            "location": loc,
            "url": j.get("absolute_url"),
            "posted_at": j.get("updated_at")
        })
    return out
