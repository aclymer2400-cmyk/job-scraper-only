import requests

BASE = "https://data.usajobs.gov/api/search"

def fetch_usajobs(cfg):
    key = cfg.get("api_key")
    if not key:
        return []
    headers = {"User-Agent": "jobhunter@example.com", "Authorization-Key": key}
    params = {"Keyword": cfg.get("query",""), "LocationName": cfg.get("location","")}
    try:
        r = requests.get(BASE, headers=headers, params=params, timeout=30)
        r.raise_for_status()
    except Exception:
        return []
    data = r.json()
    out = []
    for rj in data.get("SearchResult", {}).get("SearchResultItems", []):
        j = rj.get("MatchedObjectDescriptor", {})
        out.append({
            "id": j.get("PositionID"),
            "title": j.get("PositionTitle"),
            "company": j.get("OrganizationName"),
            "location": ", ".join([l.get("LocationName") for l in j.get("PositionLocation", [])]) if j.get("PositionLocation") else None,
            "url": j.get("PositionURI"),
            "posted_at": j.get("PublicationStartDate"),
            "salary": j.get("PositionRemuneration", [{}])[0].get("MinimumRange")
        })
    return out
