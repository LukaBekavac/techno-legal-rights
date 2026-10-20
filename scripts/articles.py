"""Cut each extraction source down to its enacting terms and build an article index.

usage: python3 -I articles.py inventory.json TEXT_DIR OUT_DIR
"""
import json, os, re, sys

inv = json.load(open(sys.argv[1]))
TXT, OUT = sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

ART = re.compile(r"^\s*(?:▼\w+\s*)?Article\s+(\d+[a-z]*)\s*$")
ANNEX = re.compile(r"^\s*(?:▼\w+\s*)?ANNEX(?:\s+[IVXLC]+)?\s*$")
ADOPTED = re.compile(r"HA(?:VE|S) ADOPTED TH(?:IS|E PRESENT)", re.I)
KW = re.compile(r"\b(right|rights|entitled|entitlement|may request|request|complain\w*|lodge|redress|remed\w+|compensation|damage|object\w*|opt[- ]?(?:in|out)|withdraw\w*|consent|choose|choice|option|access|erasure|delet\w+|rectif\w+|portab\w+|switch\w*|terminat\w+|cancel\w*|refund|reimburs\w+|repair|replacement|price reduction|contest|appeal|review|explanation|human|free of charge|notice|notif\w+|opposition|invalidity|licen[cs]e|remuneration|interest)\b", re.I)
HOLDER = re.compile(r"\b(data subjects?|natural persons?|consumers?|end-users?|users?|recipients?|individuals?|workers?|persons? performing platform work|citizens?|applicants?|right ?holders?|authors?|performers?|holders?|customers?|payers?|payees?|victims?|complainants?|business users?|creditors?|patients?|natural or legal persons?|any person|persons? concerned|affected persons?|subscribers?|viewers?|passengers?|travellers?|taxable persons?|investors?|clients?|owners?|buyers?)\b", re.I)

sources = {}
for e in inv:
    for c in e["extract_from"]:
        sources.setdefault(c, e)

summary = []
for celex, e in sources.items():
    lines = open(os.path.join(TXT, f"{celex}.txt"), encoding="utf-8").read().split("\n")
    start = 0
    for i, l in enumerate(lines):
        if ADOPTED.search(l):
            start = i
            break
    first = next((i for i in range(start, len(lines)) if ART.match(lines[i]) and ART.match(lines[i]).group(1) == "1"), None)
    if first is None:
        first = next((i for i in range(start, len(lines)) if ART.match(lines[i])), start)
    body = lines[first:]
    # cut annexes, unless annex text is the only place articles appear (amending acts quote articles inside)
    last_art = max((i for i, l in enumerate(body) if ART.match(l)), default=len(body) - 1)
    end = next((i for i in range(last_art, len(body)) if ANNEX.match(body[i])), len(body))
    body = body[:end]
    hdr = f"### {e['table_label']} | CELEX {celex} | table entry #{e['no']} ({e['status_in_table']}) | current status: {e['current_status']}"
    out_lines = [hdr, ""] + body
    open(os.path.join(OUT, f"{celex}.articles.txt"), "w").write("\n".join(out_lines))
    # index
    idx = []
    arts = [(i, ART.match(l).group(1)) for i, l in enumerate(out_lines) if ART.match(l)]
    for k, (i, num) in enumerate(arts):
        j = arts[k + 1][0] if k + 1 < len(arts) else len(out_lines)
        title = next((out_lines[x].strip() for x in range(i + 1, min(i + 4, j)) if out_lines[x].strip() and not out_lines[x].strip().startswith("▼")), "")
        chunk = "\n".join(out_lines[i:j])
        kw = len(KW.findall(chunk)); ho = len(HOLDER.findall(chunk))
        idx.append(f"Art {num:>5} | lines {i+1}-{j} | kw={kw:3d} holder={ho:3d} | {title[:110]}")
    open(os.path.join(OUT, f"{celex}.index.txt"), "w").write(hdr + "\n" + f"{len(arts)} articles; file {celex}.articles.txt has {len(out_lines)} lines\n" + "\n".join(idx) + "\n")
    summary.append((celex, e["short"], len(arts), len(out_lines), sum(len(l) for l in out_lines)))

for s in sorted(summary, key=lambda s: s[4]):
    print(f"{s[0]:12} {s[1]:28} arts={s[2]:4d} lines={s[3]:6d} chars={s[4]:8d}")
print("total chars", sum(s[4] for s in summary))
