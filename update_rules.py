#!/usr/bin/env python3
"""Build a Loon-compatible ad blocking rule list from maintained upstreams."""
from __future__ import annotations
import datetime as dt
import sys
import urllib.request

SOURCES = [
    ("Blackmatrix7 iOS Rule Script: Advertising_Domain (Loon-compatible domain list)",
     "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Advertising/Advertising_Domain.list"),
    ("fmz200 wool_scripts: rejectAd (Loon)",
     "https://raw.githubusercontent.com/fmz200/wool_scripts/main/Loon/rule/rejectAd.list"),
]
ALLOWED_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6"}
USER_AGENT = "Le672-Loon-AdBlock-Rules/1.0 (+https://github.com/Le672/Loon-AdBlock-Rules)"

def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read().decode("utf-8-sig")

def main() -> int:
    lines: dict[str, set[str]] = {}
    for name, url in SOURCES:
        text = fetch(url)
        accepted: set[str] = set()
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith(("#", ";")):
                continue
            # The companion list is one bare domain per line.
            if name.startswith("Blackmatrix7") and "," not in line:
                if " " not in line and "." in line and not line.startswith(("/", "!")):
                    accepted.add(f"DOMAIN-SUFFIX,{line.lower()}")
                continue
            if "," not in line:
                continue
            rule_type = line.split(",", 1)[0].strip().upper()
            if rule_type not in ALLOWED_TYPES:
                continue
            kind, value = line.split(",", 1)
            value = value.split(",", 1)[0].strip()
            if not value or any(ch.isspace() for ch in value):
                continue
            accepted.add(f"{kind.strip().upper()},{value}")
        if len(accepted) < 1000:
            raise RuntimeError(f"Upstream unexpectedly small ({len(accepted)} rules): {url}")
        lines[name] = accepted

    all_rules = sorted(set.union(*lines.values()), key=lambda value: (value.split(",", 1)[0], value.casefold()))
    if len(all_rules) < 10000:
        raise RuntimeError(f"Combined rule count unexpectedly small: {len(all_rules)}")
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = [
        "# NAME: Le672 Loon AdBlock Rules",
        "# DESCRIPTION: Aggregated Loon-compatible domain and IP ad/tracker blocking rules.",
        "# REPO: https://github.com/Le672/Loon-AdBlock-Rules",
        f"# UPDATED: {today}",
        f"# TOTAL: {len(all_rules)}",
    ]
    for name, url in SOURCES:
        header.append(f"# SOURCE: {name} | {url} | {len(lines[name])} rules")
    with open("AdBlock.list", "w", encoding="utf-8", newline="\n") as output:
        output.write("\n".join(header + all_rules) + "\n")
    print(f"Wrote {len(all_rules)} unique Loon rules")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Rule update failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
