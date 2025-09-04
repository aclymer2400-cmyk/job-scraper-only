import sqlite3
import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_db():
    # jobs.sqlite3 is created by schedule.yml's "Prep DB" step
    return sqlite3.connect("data/jobs.sqlite3")

def normalize_job(job):
    """Standardize a job dict before storing."""
    return {
        "id": job.get("id"),
        "title": (job.get("title") or "").strip(),
        "company": (job.get("company") or "").strip(),
        "location": (job.get("location") or "").strip(),
        "url": job.get("url"),
        "posted_at": job.get("posted_at"),
        "salary": job.get("salary"),
    }

def score_job(job, title_keywords, exclude_keywords=None):
    """
    True if title matches include keywords and doesn't match exclude keywords.
    """
    title = (job.get("title") or "").lower()

    # Exclude first
    if exclude_keywords:
        for bad in exclude_keywords:
            if bad.lower() in title:
                return False

    # If include list provided, require a hit
    if title_keywords:
        for kw in title_keywords:
            if kw.lower() in title:
                return True
        return False

    # No include list means accept all
    return True

def send_alerts(new_jobs, alerts_cfg):
    """
    Stub: prints to logs. Hook up email/Pushover later when you're ready.
    """
    if not new_jobs:
        print("No new matched jobs.")
        return

    print(f"Matched {len(new_jobs)} new jobs")
    for j in new_jobs:
        print(f"- {j['title']} @ {j['company']} [{j['location']}]")
        print(f"  {j['url']}")
