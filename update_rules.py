#!/usr/bin/env python3
"""Build a conservative Loon-compatible ad blocking rule list from upstreams."""
from __future__ import annotations

import datetime as dt
import ipaddress
import json
from pathlib import Path
import re
import sys
import urllib.request

# name, url, parser, required, reject_only
SOURCES = [
    ("Blackmatrix7 Advertising_Domain", "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Advertising/Advertising_Domain.list", "domains", True, False),
    ("fmz200 wool_scripts rejectAd", "https://raw.githubusercontent.com/fmz200/wool_scripts/main/Loon/rule/rejectAd.list", "loon", True, False),
    ("217heidai adblockfilters Loon rule 14", "https://github.com/217heidai/adblockfilters/releases/download/rule/adblockloon.list", "loon", True, False),
    ("anti-AD Surge rules", "https://anti-ad.net/surge.txt", "loon", True, False),
    ("HyperADRules Surge ads rules", "https://github.com/Lynricsy/HyperADRules/releases/latest/download/hyper_adrules_ads_surge.txt", "loon", True, False),
    ("Johnshall Shadowrocket ad-only rules", "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_ad_only.conf", "loon", True, True),
    ("nthack Shadowrocket ad rules", "https://nthack.github.io/Shadowrocket-ADBlock-Rules-Easy/sr_banlist_ad.conf", "loon", True, True),
    ("REIJI007 Adblock Rule Collection", "https://raw.githubusercontent.com/REIJI007/Adblock-Rule-Collection/main/ADBLOCK_RULE_COLLECTION_Lite.txt", "abp", False, False),
    # Selective network-rule extraction from the 2022 Bilibili recommendation index.
    ("EasyList", "https://easylist-downloads.adblockplus.org/easylist.txt", "abp", False, False),
    ("EasyList China", "https://easylist-downloads.adblockplus.org/easylistchina.txt", "abp", False, False),
    ("EasyPrivacy", "https://easylist-downloads.adblockplus.org/easyprivacy.txt", "abp", False, False),
    ("乘风 Adblock Rule", "https://gitee.com/xinggsf/Adblock-Rule/raw/master/rule.txt", "abp", False, False),
    ("Adbyby lazy rules", "https://raw.githubusercontent.com/adbyby/xwhyc-rules/master/lazy.txt", "hosts", False, False),
    ("CJX Annoyance list", "https://gitee.com/cjx82630/cjxlist/raw/master/cjx-annoyance.txt", "abp", False, False),
    ("ADgk", "https://raw.githubusercontent.com/banbendalao/ADgk/master/ADgk.txt", "abp", False, False),
]
ALLOWED_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6"}
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
ABP_DOMAIN_RE = re.compile(r"^\|\|([A-Za-z0-9.-]+)\^$")
USER_AGENT = "Le672-Loon-AdBlock-Rules/1.1 (+https://github.com/Le672/Loon-AdBlock-Rules)"


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read().decode("utf-8-sig")


def valid_domain(value: str) -> bool:
    return bool(DOMAIN_RE.fullmatch(value))


def normalize_rule(rule_type: str, value: str) -> str | None:
    rule_type = rule_type.strip().upper()
    value = value.strip()
    if rule_type not in ALLOWED_TYPES or not value:
        return None
    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
        if not valid_domain(value):
            return None
        value = value.lower()
    elif rule_type == "DOMAIN-KEYWORD":
        if any(ch.isspace() for ch in value) or len(value) > 253:
            return None
        value = value.lower()
    elif rule_type in {"IP-CIDR", "IP-CIDR6"}:
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            return None
        if (rule_type == "IP-CIDR" and network.version != 4) or (rule_type == "IP-CIDR6" and network.version != 6):
            return None
        value = str(network)
    return f"{rule_type},{value}"


def parse_lines(text: str, mode: str, reject_only: bool) -> set[str]:
    result: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "!", "[")):
            continue
        if mode == "domains":
            if "," not in line and valid_domain(line):
                result.add(f"DOMAIN-SUFFIX,{line.lower()}")
            continue
        if mode == "abp":
            match = ABP_DOMAIN_RE.fullmatch(line)
            if match and valid_domain(match.group(1)):
                result.add(f"DOMAIN-SUFFIX,{match.group(1).lower()}")
            continue
        if mode == "hosts":
            fields = line.split()
            if len(fields) >= 2 and fields[0] in {"0.0.0.0", "127.0.0.1", "::", "::1"}:
                for host in fields[1:]:
                    if valid_domain(host):
                        result.add(f"DOMAIN-SUFFIX,{host.lower()}")
            continue
        # Loon / Surge / Shadowrocket text rules. A route action is mandatory
        # for mixed files to avoid accidentally turning proxy/direct rules into blocks.
        fields = [part.strip() for part in line.split(",")]
        if len(fields) < 2:
            continue
        rule_type, value = fields[0], fields[1]
        if reject_only:
            if len(fields) < 3 or fields[2].upper() not in {"REJECT", "REJECT-DROP", "REJECT-TINYGIF", "REJECT-200"}:
                continue
        rule = normalize_rule(rule_type, value)
        if rule:
            result.add(rule)
    return result


def export_platforms(stem: str, rules: list[str], header: list[str]) -> None:
    """Export common normalized rules; unsupported types are explicitly omitted."""
    groups: dict[str, list[str]] = {}
    for rule in rules:
        kind, value = rule.split(",", 1)
        groups.setdefault(kind, []).append(value)
    def save(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        print(f"Exported {path}")
    base = Path("rules")
    base.mkdir(exist_ok=True)
    notes = "\n".join(header) + "\n"
    # Adblock domain anchors match the base domain and all its subdomains.
    # Exact DOMAIN, keyword and IP rules are omitted to preserve matching scope.
    abp = [f"||{domain}^" for domain in groups.get("DOMAIN-SUFFIX", [])]
    abp_notes = [line.replace("# ", "! ", 1) for line in header]
    save(str(base / f"{stem}.adguard.txt"), "[Adblock Plus 2.0]\n" +
         "\n".join(abp_notes + ["! Expires: 12 hours",
         "! Scope: DOMAIN-SUFFIX only; no cosmetic or script rules."] + abp) + "\n")
    save(str(base / f"{stem}.surge.list"), notes + "\n".join(rules) + "\n")
    save(str(base / f"{stem}.clash.yaml"), notes + "payload:\n" +
         "\n".join("  - " + json.dumps(rule) for rule in rules) + "\n")
    qx_types = {"DOMAIN": "HOST", "DOMAIN-SUFFIX": "HOST-SUFFIX",
                "DOMAIN-KEYWORD": "HOST-KEYWORD", "IP-CIDR": "IP-CIDR",
                "IP-CIDR6": "IP6-CIDR"}
    save(str(base / f"{stem}.quantumultx.list"), notes + "\n".join(
         f"{qx_types[kind]},{value},REJECT" for kind, values in groups.items()
         for value in values) + "\n")
    fields = {"DOMAIN": "domain", "DOMAIN-SUFFIX": "domain_suffix",
              "DOMAIN-KEYWORD": "domain_keyword"}
    # Separate objects are ORed. Fields inside one object would be ANDed.
    sing_rules = [{field: groups[kind]} for kind, field in fields.items() if groups.get(kind)]
    ips = groups.get("IP-CIDR", []) + groups.get("IP-CIDR6", [])
    if ips:
        sing_rules.append({"ip_cidr": ips})
    save(str(base / f"{stem}.sing-box.json"),
         json.dumps({"version": 1, "rules": sing_rules}, ensure_ascii=False, indent=2) + "\n")
    domains = sorted(set(groups.get("DOMAIN", []) + groups.get("DOMAIN-SUFFIX", [])))
    save(str(base / f"{stem}.hosts.txt"), notes +
         "# Hosts entries match only the listed hostname, not arbitrary subdomains.\n" +
         "\n".join(f"0.0.0.0 {domain}" for domain in domains) + "\n")
    save(str(base / f"{stem}.domains.txt"), notes +
         "# Exact hostnames only; wildcard suffix semantics are not retained.\n" +
         "\n".join(domains) + "\n")


def write_list(filename: str, label: str, selected_names: list[str], by_source: dict[str, set[str]], source_notes: list[str], failures: list[str], updated: str) -> int:
    selected = {name: rules for name, rules in by_source.items() if name in selected_names}
    if not selected:
        raise RuntimeError(f"No usable sources for {filename}")
    all_rules = sorted(set.union(*selected.values()), key=lambda value: (value.split(",", 1)[0], value.casefold()))
    if len(all_rules) < 10000:
        raise RuntimeError(f"Combined rule count unexpectedly small for {filename}: {len(all_rules)}")
    header = [
        f"# NAME: Le672 Loon AdBlock Rules {label}".rstrip(),
        "# DESCRIPTION: Aggregated Loon-compatible domain and IP ad/tracker blocking rules.",
        "# REPO: https://github.com/Le672/Loon-AdBlock-Rules",
        f"# UPDATED: {updated}",
        f"# TOTAL: {len(all_rules)}",
        *(note for note in source_notes if any(note.startswith(f"# SOURCE: {name} |") for name in selected)),
    ]
    for failure in failures:
        header.append(f"# OPTIONAL SOURCE SKIPPED: {failure}")
    with open(filename, "w", encoding="utf-8", newline="\n") as output:
        output.write("\n".join(header + all_rules) + "\n")
    export_platforms("adblock-extended" if label else "adblock", all_rules, header)
    print(f"Wrote {filename}: {len(all_rules)} unique rules from {len(selected)} sources")
    return len(all_rules)


def main() -> int:
    by_source: dict[str, set[str]] = {}
    source_notes: list[str] = []
    failures: list[str] = []
    for name, url, mode, required, reject_only in SOURCES:
        try:
            text = fetch(url)
            rules = parse_lines(text, mode, reject_only)
            minimum = 100 if mode in {"domains", "loon"} else 10
            if len(rules) < minimum:
                raise RuntimeError(f"only {len(rules)} compatible rules")
            by_source[name] = rules
            source_notes.append(f"# SOURCE: {name} | {url} | {len(rules)} rules")
            print(f"{name}: {len(rules)}")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            print(f"Skipped {name}: {exc}", file=sys.stderr)
            if required:
                raise RuntimeError(f"Required source failed; keeping previous lists. {name}: {exc}") from exc

    if len(by_source) < 7:
        raise RuntimeError(f"Too few usable upstreams: {len(by_source)}")
    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    core_sources = [
        "Blackmatrix7 Advertising_Domain",
        "fmz200 wool_scripts rejectAd",
        "anti-AD Surge rules",
        "HyperADRules Surge ads rules",
        "Johnshall Shadowrocket ad-only rules",
        "nthack Shadowrocket ad rules",
        "ADgk",
    ]
    write_list("AdBlock.list", "", core_sources, by_source, source_notes, failures, updated)
    write_list("AdBlock-Extended.list", "Extended", list(by_source), by_source, source_notes, failures, updated)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Rule update failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
