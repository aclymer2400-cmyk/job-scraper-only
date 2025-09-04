import sqlite3
import yaml
import json

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_db():
    conn = sqlite3.connect("data/jobs.sqlite3")
    return conn

def normalize_job(job):
    """Standardize job dict fields before storing."""
    return {
        "id": job.get("id"),
        "title": job.get("title", "").strip(),
        "company": job.get("company", "").strip(),
        "location": job.get("location", "").strip(),
        "url": job.get("url"),
        "posted_at": job.get("posted_at"),
        "salary": job.get("salary"),
    }

def score_job(job, title_keywords):
    """
    Return True if job title contains one of the title keywords.
    If no keywords are provided, always return True.
    """
    if not title_keywords:
        return True  # no filters, accept all jobs

    title = (job.get("title") or "").lower()
    for keyword in title_keywords:
        if keyword.lower() in title:
            return True
    return False

def send_alerts(new_jobs, alerts_cfg):
    """Placeholder alert system (email/Pushover later)."""
    print(f"Matched {len(new_jobs)} new jobs")
    for job in new_jobs:
        print(f"- {job['title']} @ {job['company']} ({job['location']})")
        print(f"  {job['url']}")
