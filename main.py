#!/usr/bin/env python3
import argparse, json, time
from utils import load_config, get_db, normalize_job, score_job, send_alerts
from scrapers.greenhouse import fetch_greenhouse
from scrapers.lever import fetch_lever
from scrapers.usajobs import fetch_usajobs

def store_job(cur, source, job):
    sql = "INSERT OR IGNORE INTO jobs (source, job_id, title, company, location, url, posted_at, salary, raw) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.execute(sql, (source, job["id"], job["title"], job.get("company"), job.get("location"),
                      job["url"], job.get("posted_at"), job.get("salary"), json.dumps(job)))
    return cur.rowcount == 1

def scrape_once(cfg, conn):
    cur = conn.cursor()
    new_hits = []
    for company in cfg.get("sources", {}).get("greenhouse", {}).get("companies", []):
        for job in fetch_greenhouse(company):
            job_n = normalize_job(job)
            if store_job(cur, f"greenhouse:{company}", job_n):
                new_hits.append(job_n)
    for company in cfg.get("sources", {}).get("lever", {}).get("companies", []):
        for job in fetch_lever(company):
            job_n = normalize_job(job)
            if store_job(cur, f"lever:{company}", job_n):
                new_hits.append(job_n)
    if cfg.get("sources", {}).get("usajobs", {}).get("enabled"):
        for job in fetch_usajobs(cfg["sources"]["usajobs"]):
            job_n = normalize_job(job)
            if store_job(cur, "usajobs", job_n):
                new_hits.append(job_n)
    conn.commit()
    matched = [j for j in new_hits if score_job(j, cfg.get("title_keywords", {}), cfg.get("location_filters", []))]
    if matched:
        send_alerts(matched, cfg.get("alerts", {}))
    print(f"Scrape done. New: {len(new_hits)} | Matched filters: {len(matched)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["scrape","loop","initdb"])
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    conn = get_db()
    if args.command == "initdb":
        with open("data/schema.sql","r") as f:
            conn.executescript(f.read())
        print("DB initialized.")
        return
    if args.command == "scrape":
        scrape_once(cfg, conn)
    if args.command == "loop":
        while True:
            scrape_once(cfg, conn)
            time.sleep(60 * int(cfg.get("poll_interval_minutes", 15)))

if __name__ == "__main__":
    main()
