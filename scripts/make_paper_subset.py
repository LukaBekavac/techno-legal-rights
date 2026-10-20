"""Derive the paper's sample from the full catalogue: every right in the twelve acts analysed in the paper,
with the author's two changes. Checks the result against the numbers reported in the paper.

usage: python3 scripts/make_paper_subset.py   (run from the repository root)
"""
import collections
import csv
import json

SRC = "data/all-112-texts/rights_catalogue.json"
OUT = "data/paper-12-acts/rights_12_acts"

ACTS = {
    "32016R0679": "General Data Protection Regulation",
    "32022R2065": "Digital Services Act",
    "32022R1925": "Digital Markets Act",
    "32023R2854": "Data Act",
    "32024R1689": "AI Act",
    "32011L0083": "Consumer Rights Directive",
    "32019L0770": "Digital Content Directive",
    "32024R2847": "Cyber Resilience Act",
    "32025R0327": "European Health Data Space Regulation",
    "32015L2366": "Payment Services Directive",
    "32014R0910": "European Digital Identity Regulation",
    "32019L0790": "Directive on Copyright in the Digital Single Market",
}

# The author's changes to the model's classification (Appendix A.1, step 7).
DROP = {"R1623": "Art. 53(1)(c) AI Act is counted together with the reservation under Art. 4(3) CDSM (R1064), to which it gives effect."}
FAMILY = {"R0983": ("portability & interoperability",
                    "Art. 7(7) DMA: family changed from 'consent & objection'; the level stays CLICK.")}

rights = json.load(open(SRC, encoding="utf-8"))
sample = []
for r in rights:
    if r["celex"] not in ACTS or r["id"] in DROP:
        continue
    r = dict(r)
    note = ""
    if r["id"] in FAMILY:
        r["tl_family"], note = FAMILY[r["id"]]
    checked = r["techno_legal"] in ("techno-legal", "borderline")
    r["author_checked"] = "yes" if checked else "no"
    r["author_note"] = note
    sample.append(r)

# The numbers reported in the paper (Section 4.3, Tables 3 to 5).
tl = [r for r in sample if r["techno_legal"] == "techno-legal"]
classes = collections.Counter(r["techno_legal"] for r in sample)
levels = collections.Counter(r["tl_level"] for r in tl)
assert len(sample) == 497, len(sample)
assert classes == {"techno-legal": 79, "borderline": 90, "digitized": 97, "no": 231}, classes
assert [levels[l] for l in ("CLICK", "READ", "OPERATE", "BUILD")] == [20, 13, 41, 5], levels
assert sum(r["tl_scope"] == "everyday" for r in tl) == 76

json.dump(sample, open(OUT + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
head = list(sample[0].keys())
with open(OUT + ".csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(head)
    for r in sample:
        w.writerow([r.get(h, "") for h in head])

print(len(sample), "rights;", dict(classes), "; levels", dict(levels))
print(collections.Counter(r["tl_family"] for r in tl))
