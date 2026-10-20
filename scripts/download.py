"""Download every document in the inventory from the EU Publications Office (Cellar).

usage: python3 -I download.py inventory.json OUT_DIR TEXT_DIR
"""
import json, os, re, sys, html, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

TODAY = "20261009"
inv = json.load(open(sys.argv[1]))
OUT, TXT = sys.argv[2], sys.argv[3]
STATUS_DIR = {"applicable": "1_applicable", "in_negotiation": "2_in_negotiation", "planned": "3_planned"}
UA = {"User-Agent": "Mozilla/5.0 (research download)"}
SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"


def get(url, accept=None):
    h = dict(UA)
    if accept:
        h["Accept"] = accept
        h["Accept-Language"] = "eng"
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()
    except Exception as e:
        return 0, "", str(e).encode()


def latest_consolidated(celex):
    q = f'''PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?c WHERE {{ ?a cdm:resource_legal_id_celex "{celex}"^^<http://www.w3.org/2001/XMLSchema#string> .
?k cdm:act_consolidated_consolidates_resource_legal ?a . ?k cdm:resource_legal_id_celex ?c . }}'''
    # python.org builds on macOS lack a CA bundle, so the https SPARQL call goes through curl
    import subprocess
    r = subprocess.run(["curl", "-sS", "-G", SPARQL, "--data-urlencode", "query=" + q,
                        "--data-urlencode", "format=application/sparql-results+json"], capture_output=True)
    body = r.stdout
    if r.returncode != 0 or not body.startswith(b"{"):
        raise RuntimeError(f"SPARQL failed for {celex}: {r.stderr[:200]}")
    vals = [b["c"]["value"] for b in json.loads(body)["results"]["bindings"]]
    mine = sorted(v for v in vals if v.startswith("0" + celex[1:] + "-"))
    current = [v for v in mine if v.split("-")[1] <= TODAY]
    return (current[-1] if current else None), mine


def fetch(celex, accepts):
    """Return list of (content_type, bytes) items, following 300 multiple-choice lists."""
    for acc in accepts:
        st, ct, body = get(f"http://publications.europa.eu/resource/celex/{celex}", acc)
        if st == 200 and len(body) > 500:
            return [(ct, body)], acc
        if st == 300:
            links = re.findall(r'href="(http://publications\.europa\.eu/resource/cellar/[^"]+)"', body.decode("utf-8", "ignore"))
            items = []
            for l in links:
                s2, c2, b2 = get(l, acc)
                if s2 == 200 and len(b2) > 500:
                    items.append((c2, b2))
            if items:
                return items, acc
    return [], None


def to_text(raw):
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|tr|li|h\d|table)>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", " \t ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t ]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


HTML_ACCEPTS = ["application/xhtml+xml", "text/html"]
PDF_ACCEPTS = ["application/pdf;type=pdfa1a", "application/pdf;type=pdfa2a", "application/pdf", "application/pdf;type=pdfx", "application/pdf;type=pdf1x"]


def do_doc(entry, doc):
    folder = os.path.join(OUT, STATUS_DIR[entry["status_in_table"]], f'{entry["no"]:03d}_{entry["short"]}')
    os.makedirs(folder, exist_ok=True)
    celex = doc["celex"]
    version, all_cons = (None, [])
    if celex[0] == "3":
        version, all_cons = latest_consolidated(celex)
    use = version or celex
    rec = dict(no=entry["no"], short=entry["short"], role=doc["role"], celex=celex, version_downloaded=use,
               consolidated_versions_available=all_cons, files=[], text_file=None, errors=[])
    base = f'{entry["short"]}_{doc["role"]}_{use}'
    items, acc = fetch(use, HTML_ACCEPTS)
    if not items and use != celex:  # consolidated text missing -> original
        use = celex; base = f'{entry["short"]}_{doc["role"]}_{use}'; rec["version_downloaded"] = use
        items, acc = fetch(use, HTML_ACCEPTS)
    texts = []
    for i, (ct, body) in enumerate(items, 1):
        fn = os.path.join(folder, base + (f"_part{i}" if len(items) > 1 else "") + ".html")
        open(fn, "wb").write(body)
        rec["files"].append(os.path.relpath(fn, OUT))
        texts.append(to_text(body))
    if not items:
        rec["errors"].append("no HTML manifestation found")
    pdfs, pacc = fetch(use, PDF_ACCEPTS)
    for i, (ct, body) in enumerate(pdfs, 1):
        if not body.startswith(b"%PDF"):
            continue
        fn = os.path.join(folder, base + (f"_part{i}" if len(pdfs) > 1 else "") + ".pdf")
        open(fn, "wb").write(body)
        rec["files"].append(os.path.relpath(fn, OUT))
    if not any(f.endswith(".pdf") for f in rec["files"]):
        rec["errors"].append("no PDF manifestation found")
    if texts:
        tf = os.path.join(TXT, f"{celex}.txt")
        hdr = f"### {entry['table_label']} | CELEX {celex} | text version {use} | role {doc['role']}\n"
        open(tf, "w").write(hdr + "\n\n".join(texts))
        rec["text_file"] = os.path.relpath(tf, OUT)
    print(f'{entry["no"]:3d} {entry["short"]:28} {doc["role"]:9} {use:22} files={len(rec["files"])} {"ERR " + "; ".join(rec["errors"]) if rec["errors"] else ""}', flush=True)
    return rec


os.makedirs(TXT, exist_ok=True)
jobs = [(e, d) for e in inv for d in e["docs"]]
with ThreadPoolExecutor(6) as ex:
    results = list(ex.map(lambda j: do_doc(*j), jobs))
# planned items with nothing to download: leave a note
for e in inv:
    if not e["docs"]:
        folder = os.path.join(OUT, STATUS_DIR[e["status_in_table"]], f'{e["no"]:03d}_{e["short"]}')
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "NO_LEGAL_TEXT.txt"), "w").write(f'{e["table_label"]}\nStatus (checked 2026-10-09): {e["current_status"]}\nNo Commission proposal or adopted text exists to download.\n')
json.dump(results, open(os.path.join(OUT, "download_manifest.json"), "w"), indent=1)
print("done:", len(results), "documents;", sum(1 for r in results if r["errors"]), "with errors")
