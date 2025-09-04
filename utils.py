import os, smtplib, requests, json, sqlite3, yaml

DB_PATH = "data/jobs.sqlite3"

def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_db():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def _contains_any(text, keywords):
    text = (text or "").lower()
    return any(k.lower() in text for k in keywords)

def normalize_job(job):
    return {
        "id": str(job.get("id") or job.get("reqid") or job.get("url")),
        "title": (job.get("title") or "").strip(),
        "company": (job.get("company") or "").strip() if job.get("company") else None,
        "location": (job.get("location") or "").strip() if job.get("location") else None,
        "url": job.get("url"),
        "posted_at": job.get("posted_at"),
        "salary": job.get("salary")
    }

def score_job(job, title_keywords, location_filters):
    title = job.get("title","")
    location = job.get("location","")
    include = title_keywords.get("include", [])
    exclude = title_keywords.get("exclude", [])
    title_ok = (_contains_any(title, include) if include else True) and not _contains_any(title, exclude)
    loc_ok = True if not location_filters else _contains_any(location, location_filters) or "remote" in (location or "").lower()
    return title_ok and loc_ok

def send_alerts(items, cfg):
    if cfg.get("email", {}).get("enabled"):
        _send_email(items, cfg["email"])
    if cfg.get("pushover", {}).get("enabled"):
        _send_pushover(items, cfg["pushover"])

def _send_email(items, ecfg):
    lines = []
    for j in items:
        lines.append(f"{j.get('title')} at {j.get('company')} [{j.get('location')}]")
        lines.append(j.get("url"))
        lines.append("")
    payload = "\n".join(lines)
    msg = f"Subject: [JobBot] {len(items)} new matches\nFrom: {ecfg['smtp_user']}\nTo: {ecfg['to']}\n\n{payload}"
    with smtplib.SMTP(ecfg["smtp_host"], ecfg.get("smtp_port",587)) as s:
        s.starttls()
        s.login(ecfg["smtp_user"], ecfg["smtp_pass"])
        s.sendmail(ecfg["smtp_user"], [ecfg["to"]], msg)

def _send_pushover(items, pcfg):
    text = "\n".join(f"{j.get('title')} at {j.get('company')}\n{j.get('url')}" for j in items[:5])
    try:
        requests.post("https://api.pushover.net/1/messages.json", data={
            "token": pcfg["api_token"],
            "user": pcfg["user_key"],
            "message": text[:1024],
            "title": f"{len(items)} new matches"
        }, timeout=15)
    except Exception:
        pass
