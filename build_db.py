#!/usr/bin/env python3
"""Build rules.json for the Sigma Rule Searcher artifact.

Usage: python3 build_db.py <path-to-sigma-clone> <output-json>
Collects every .yml under the rule folders of SigmaHQ/sigma and writes a
compact JSON database (metadata + raw YAML) used by the web page.
"""
import datetime
import json
import os
import subprocess
import sys

import yaml

FOLDERS = [
    "rules",
    "rules-emerging-threats",
    "rules-threat-hunting",
    "rules-compliance",
    "rules-placeholder",
    "rules-dfir",
    "deprecated",
    "unsupported",
]


def s(v):
    if v is None:
        return ""
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return str(v)


def lst(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [s(x) for x in v if x is not None]
    return [s(v)]


def main(repo, out):
    rules, errors = [], 0
    for folder in FOLDERS:
        base = os.path.join(repo, folder)
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for fn in sorted(files):
                if not fn.endswith((".yml", ".yaml")):
                    continue
                full = os.path.join(root, fn)
                with open(full, encoding="utf-8", errors="replace") as f:
                    raw = f.read()
                try:
                    doc = next(iter(yaml.safe_load_all(raw)), None) or {}
                    if not isinstance(doc, dict):
                        doc = {}
                except Exception:
                    doc, errors = {}, errors + 1
                ls = doc.get("logsource") or {}
                if not isinstance(ls, dict):
                    ls = {}
                rel = os.path.relpath(full, repo).replace(os.sep, "/")
                rules.append({
                    "i": s(doc.get("id")),
                    "t": s(doc.get("title")) or fn,
                    "st": s(doc.get("status")),
                    "lv": s(doc.get("level")),
                    "d": s(doc.get("description")).strip(),
                    "a": s(doc.get("author")),
                    "dt": s(doc.get("date")),
                    "md": s(doc.get("modified")),
                    "tg": lst(doc.get("tags")),
                    "pr": s(ls.get("product")),
                    "ca": s(ls.get("category")),
                    "sv": s(ls.get("service")),
                    "rf": lst(doc.get("references")),
                    "fp": lst(doc.get("falsepositives")),
                    "f": folder,
                    "p": rel,
                    "y": raw,
                })
    rules.sort(key=lambda r: (FOLDERS.index(r["f"]), r["t"].lower()))

    commit, commit_date = "", ""
    try:
        commit = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
        commit_date = subprocess.check_output(["git", "-C", repo, "log", "-1", "--format=%cI"], text=True).strip()
    except Exception:
        pass

    db = {
        "meta": {
            "source": "https://github.com/SigmaHQ/sigma",
            "commit": commit,
            "commitDate": commit_date,
            "builtAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "count": len(rules),
            "parseErrors": errors,
        },
        "rules": rules,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))
    # small version stamp the page checks before downloading the full database
    with open(os.path.join(os.path.dirname(os.path.abspath(out)), "version.json"), "w", encoding="utf-8") as f:
        json.dump(db["meta"], f, ensure_ascii=False)
    print(f"wrote {len(rules)} rules ({errors} parse errors) -> {out} ({os.path.getsize(out)/1e6:.2f} MB)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
