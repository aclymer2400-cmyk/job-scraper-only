import requests

def fetch_lever(company_shortname):
    url = f"https://api.lever.co/v0/postings/{company_shortname}?mode=json"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except Exception:
        return []
    data = r.json()
    out = []
    for j in data:
        loc = j.get("categories", {}).get("location")
        out.append({
            "id": j.get("id"),
            "title": j.get("text"),
            "company": company_shortname,
            "location": loc,
            "url": j.get("hostedUrl") or j.get("applyUrl"),
            "posted_at": j.get("createdAt")
        })
    return out
