"""Combine the batch classifications and apply the cross-batch consistency overrides.
usage: merge_tl.py TL_DIR   (reads TL_DIR/out/B*.json, writes TL_DIR/final/all.json)"""
import json, sys, glob, os, collections

tl_dir = sys.argv[1]
rows = []
for f in sorted(glob.glob(os.path.join(tl_dir, "out", "B*.json"))):
    rows += json.load(open(f))
by = {x["id"]: x for x in rows}
assert len(by) == len(rows)

# 1. Telephone service functions: a phone call counts as non-technical (rule used in B05, applied to the DNA rows in B06).
PHONE = {"R1944": "Reaching numbers is ordinary calling.", "R1989": "Calling the hotline is an ordinary phone call.",
         "R1990": "Calling 112 is an ordinary phone call.", "R1992": "Equivalent access is provided by the service; the holder just calls."}
# 2. Consent or refusal where the law requires no interface function: a letter or simply not consenting still works
#    (same reading as GDPR Art. 7(3) and 21 in B01).
CONSENT = ["R1329", "R1354", "R0957", "R1701"]
# 3. Technical access rights of competitors, suppliers, applicants or researchers who are not the governed party
#    in a digital relationship (rule used in B03 and B07).
HOLDER = ["R0050", "R0052", "R0053", "R0055", "R1388", "R0730", "R1610", "R0148", "R0174", "R0201", "R1572",
          "R1657", "R1926", "R1466", "R0625", "R0633", "R0636"]
# 4. Public warnings are a required electronic message with a plain result (rule used for the EECC row in B05).
WARN = ["R1993"]

changed = []
def setv(i, **kw):
    x = by[i]
    old = (x["tl"], x["level"])
    x.update(kw)
    changed.append((i, old, (x["tl"], x["level"])))

for i, why in PHONE.items():
    setv(i, tl="digitized", level="", family="", reason=f"{why} Test: yes (a phone call works without technical skill). Consistency pass.")
for i in CONSENT:
    x = by[i]
    setv(i, tl="borderline", reason=(x["reason"].rstrip(".") + ". Consistency pass: no interface function required; refusing or a letter still works.")[:400])
for i in HOLDER:
    x = by[i]
    setv(i, tl="borderline", reason=(x["reason"].rstrip(".") + ". Consistency pass: holder is not the governed party.")[:400])
for i in WARN:
    setv(i, tl="borderline", level="READ")

os.makedirs(os.path.join(tl_dir, "final"), exist_ok=True)
json.dump(rows, open(os.path.join(tl_dir, "final", "all.json"), "w"), ensure_ascii=False, indent=0)
for c in changed:
    print(*c)
print(len(changed), "changed")
print(collections.Counter(x["tl"] for x in rows))
print(collections.Counter(x["level"] for x in rows if x["tl"] == "techno-legal"))
print("everyday techno-legal", sum(1 for x in rows if x["tl"] == "techno-legal" and x["scope"] == "everyday"))
