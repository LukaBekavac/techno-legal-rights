"""Build the browsable website (docs/index.html) from the catalogue, the paper's sample and site/template.html.

usage: python3 scripts/build_site.py   (run from the repository root, after make_paper_subset.py)
"""
import collections
import json

import openpyxl

ALL = "data/all-112-texts/"
inv = json.load(open(ALL + "inventory.json", encoding="utf-8"))
rights = json.load(open(ALL + "rights_catalogue.json", encoding="utf-8"))
sample = {r["id"]: r for r in json.load(open("data/paper-12-acts/rights_12_acts.json", encoding="utf-8"))}
wb = openpyxl.load_workbook(ALL + "rights_catalogue.xlsx", read_only=True)
laws = list(wb["Laws"].iter_rows(values_only=True))[1:]

PAPER_ACTS = {"32016R0679", "32022R2065", "32022R1925", "32023R2854", "32024R1689", "32011L0083", "32019L0770",
              "32024R2847", "32025R0327", "32015L2366", "32014R0910", "32019L0790"}
DROPPED = {"R1623": "In the paper, counted together with the reservation under Art. 4(3) CDSM (R1064), to which it gives effect."}


def now_class(e):
    s = e["current_status"]
    if s.startswith("Adopted"): return "Adopted"
    if s.startswith("Withdrawn"): return "Withdrawn"
    if s.startswith(("Not proposed", "Not yet proposed", "No stand-alone")): return "Not proposed"
    if s.startswith(("Pending", "Proposed", "Provisional")):
        return "Proposed" if e["status_in_table"] == "planned" else "Pending"
    if "replaced by" in s: return "Replaced"
    if "re-adopted" in s: return "Re-adopted"
    return "In force"


texts = collections.defaultdict(list)
for row in laws:
    no, _, _, _, _, _, celex, act, n, comment = row
    if celex:
        texts[no].append({"c": celex, "n": act, "k": n or 0, "m": comment or ""})

entries = [{
    "no": e["no"], "st": e["status_in_table"], "area": e["category"], "label": e["table_label"],
    "refs": e["table_refs"], "cur": e["current_status"], "now": now_class(e), "texts": texts.get(e["no"], []),
} for e in inv]

acts, cats = {}, [c for c, _ in collections.Counter(r["category"] for r in rights).most_common()]
KIND = {"individual": 0, "any person": 1, "organisation": 2}
TL = {"techno-legal": 0, "borderline": 1, "digitized": 2, "no": 3}
SCOPE = {"everyday": 0, "specialist": 1, "business": 2}
out = []
for r in rights:
    assert r["quote_verified"] and r["article_verified"]
    acts.setdefault(r["celex"], {"n": r["act"], "e": r["eurlex"], "s": r["source_legal_status"], "i": r["instrument"]})
    s = sample.get(r["id"])
    c = s or r  # the author's corrections apply to rights in the paper's sample
    out.append({
        "id": r["id"], "no": r["entry_no"], "c": r["celex"], "a": r["article"], "r": r["right"],
        "h": r["rightholder"], "k": KIND[r["holder_kind"]], "to": r["addressee"], "cat": cats.index(r["category"]),
        "d": r["description"], "x": r["exercise"], "ex": 1 if r["explicit"] else 0, "q": r["quote"],
        "f": r["applies_from"], "nt": r["notes"], "ef": r["in_effect_today"],
        "tl": TL[c["techno_legal"]], "sc": SCOPE[c["tl_scope"]], "lv": c["tl_level"] or "", "fam": c["tl_family"] or "",
        "why": c["tl_reason"] or "",
        # v: 1 = in the paper's sample of twelve acts; ck: 1 = classification checked by the author
        "v": 1 if s else 0, "ck": 1 if s and s["author_checked"] == "yes" else 0,
        "pn": (s["author_note"] if s else DROPPED.get(r["id"], "")),
    })

assert sum(x["v"] for x in out) == 497 and sum(x["ck"] for x in out) == 169
data = {"checked": "9 Oct 2026", "cats": cats, "entries": entries, "acts": acts, "rights": out}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open("site/template.html", encoding="utf-8").read()
assert html.count("/*DATA*/") == 1
open("docs/index.html", "w", encoding="utf-8").write(html.replace("/*DATA*/", blob))
print("entries", len(entries), "acts", len(acts), "rights", len(out), "in sample", sum(x["v"] for x in out))
