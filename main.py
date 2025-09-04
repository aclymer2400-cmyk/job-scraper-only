#!/usr/bin/env python3
import argparse
import json
import time

from utils import load_config, get_db, normalize_job, score_job, send_alerts
from scrapers.greenhouse import fetch_greenhouse
from scrapers.lever import fetch_lever
from scrapers.usajobs import fetch_usajobs
from scrapers.ziprecruiter import fetch_ziprecruiter  # you added this file

def store_job(cur, source, job):
    sql = """
    INSERT OR IGNORE INTO jobs
        (source, job_id, title, company, location, url, posted_at, salary, raw)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    raw = json.dumps(job, ensure_ascii=False)
    cur.execute(
        sql,
        (
            source,
            job.get("id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("url"),
            job.get("posted_at"),
            job.get("salary"),
            raw,
        ),
    )
    return cur.rowcount == 1

def scrape_once(cfg, conn):
    cur = conn.cursor()
    new_hits = []

    includes = cfg.get("title_keywords", [])      # list
    excludes = cfg.get("exclude", [])             # list

    # 1) Greenhouse
    for company in cfg.get("sources", {}).get("greenhouse", {}).get("companies", []):
        for j in fetch_greenhouse(company):
            jn = normalize_job(j)
            if score_job(jn, includes, excludes) and store_job(cur, f"greenhouse:{company}", jn):
                new_hits.append(jn)

    # 2) Lever
    for company in cfg.get("sources", {}).get("lever", {}).get("companies", []):
        for j in fetch_lever(company):
            jn = normalize_job(j)
            if score_job(jn, includes, excludes) and store_job(cur, f"lever:{company}", jn):
                new_hits.append(jn)

    # 3) USAJobs (optional)
    us = cfg.get("usajobs", {})
    if us.get("enabled"):
        for j in fetch_usajobs(us):
            jn = normalize_job(j)
            if score_job(jn, includes, excludes) and store_job(cur, "usajobs", jn):
                new_hits.append(jn)

    # 4) ZipRecruiter (optional)
    zr = cfg.get("ziprecruiter", {})
    if zr.get("enabled"):
        for j in fetch_ziprecruiter(zr):
            jn = normalize_job(j)
            if score_job(jn, includes, excludes) and store_job(cur, "ziprecruiter", jn):
                new_hits.append(jn)

    conn.commit()

    # Alert only the ones that passed filters
    if new_hits:
        send_alerts(new_hits, cfg.get("alerts", {}))

    print(f"Scrape done. New: {len(new_hits)} | Matched filters: {len(new_hits)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["scrape", "loop", "initdb"])
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    conn = get_db()

    if args.command == "initdb":
        # schedule.yml already runs schema.sql, but keep this for local use
        print("DB initialized.")
        return

    if args.command == "scrape":
        scrape_once(cfg, conn)
        return

    if args.command == "loop":
        while True:
            scrape_once(cfg, conn)
            time.sleep(60 * int(cfg.get("poll_interval_minutes", 15)))

if __name__ == "__main__":
    main()
