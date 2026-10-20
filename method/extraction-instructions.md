# Rights extraction from EU digital legislation: shared instructions

You are one of several agents extracting **rights that individuals or other persons can exercise** from EU legal acts.
The user's own examples of what counts: **GDPR Art. 16** (right to rectification) and **DSA Art. 38** (users of very
large platforms must be offered at least one recommender-system option not based on profiling). Note that DSA 38 is phrased
as a provider obligation, yet it gives the user a choice they can exercise. Both kinds count.

## Inputs
For each CELEX number assigned to you, two files exist in
`<workdir>/extract/`:
- `<CELEX>.index.txt`: one line per article with its line range in the articles file, keyword counts (`kw` = rights-type
  words, `holder` = words such as consumer/user/data subject), and the article title. The header line gives the act's name,
  its table entry number, and its current status.
- `<CELEX>.articles.txt`: the enacting terms only (recitals and annexes removed). This is the consolidated version in force where one exists;
  for Commission proposals (CELEX 5…PC…) it is the proposed text.

How to read: always open the index first. If an articles file has fewer than ~700 lines, read it all. Otherwise read every
article whose title, or whose kw/holder counts, suggests it might confer something on persons (users, consumers, data subjects,
workers, applicants, rightholders, businesses, complainants, victims…). Also read any article on complaints, redress, remedies,
penalties-with-compensation, or information to persons, and any provider/trader obligation owed to an identifiable person.
Use the Read tool with `offset`/`limit` taken from the index line ranges. Rights-heavy acts (GDPR, DSA, CRD, EECC, AI Act, PSD2,
Data Act, EHDS, DMA, Platform Work, CDSM …) deserve a full read of the relevant chapters. For acts that confer
almost nothing (funding programmes, block exemptions, technical acts), skim the index, spot-check likely articles, and record
"0 rights" with a short reason.

## What counts as a right (inclusion test)
Include a provision if a natural or legal person (other than a public authority acting as such, a Member State, an EU body or the
Commission) can actively invoke, exercise or claim something under it:
1. **Express rights/entitlements**: "shall have the right", "is entitled", "may request / require / lodge / object / withdraw /
   terminate / opt / choose / contest", exclusive rights (IP), rights to remuneration, compensation, interest, refunds.
2. **Actionable options or requests built into another party's duty**: e.g. DSA 16 notice-and-action, DSA 20 internal complaint,
   DSA 38 non-profiling option, P2B internal complaint handling, CRD withdrawal, switching or porting, free-of-charge termination,
   on-request explanations, human review or contact points that persons can use.
3. **Individualised information or notification owed to an identifiable person**, which they receive and can rely on
   (e.g. GDPR 13/14, DSA 17 statement of reasons, P2B 4 statement of reasons, notification of a data breach to the data subject).
4. **Remedies**: complaint to an authority, out-of-court dispute settlement, judicial remedy, collective/representative action,
   compensation and liability claims, rights of defence/procedural rights of undertakings (be heard, access to file).

Exclude: general compliance duties (security, risk management, conformity, CE marking) without a person-facing actionable element;
public, non-individual transparency (annual reports, public registers), unless the person has a right to request something;
powers of authorities; rights of Member States, EU institutions or the Commission; definitions; scope/derogation clauses;
and provisions that merely preserve other law ("without prejudice to…").

Granularity: one record per **distinct, independently exercisable right**. Usually that is one per article, or one per paragraph
when paragraphs grant different rights (e.g. GDPR 15(1) access and 15(3) copy may be separate; GDPR 22 is one record plus one
for the safeguards right to human intervention/contest). Do not split a single right into its sub-points or conditions.
Amending acts (e.g. an act inserting Art. 5a into another directive): cite the provision as inserted, e.g.
"Art. 5a Dir 2013/11/EU (inserted by Art. 1(4))".
If a right is merely a cross-reference reproducing a right that another act in the same file already grants, still record it, because
each act is catalogued separately.

## Output
Write ONE JSON file: `<workdir>/rights/<GROUP>.json`
with this structure (use the Write tool, then validate with
`python3 -I -c "import json,sys; d=json.load(open(sys.argv[1])); print(len(d['rights']))" <file>`):

```json
{
  "group": "G01",
  "sources": [
    {"celex": "32016R0679", "entry_no": 23, "act": "GDPR", "rights_found": 31,
     "articles_read": "Arts 1-99 index; full read of Ch. III, VIII, Arts 7, 8, 34", "comment": "core data-subject rights"}
  ],
  "rights": [
    {
      "entry_no": 23,
      "celex": "32016R0679",
      "act": "GDPR",
      "article": "Art. 16",
      "right": "Right to rectification",
      "rightholder": "data subject",
      "holder_kind": "individual",
      "addressee": "controller",
      "category": "Rectification, erasure & restriction",
      "description": "Obtain without undue delay the rectification of inaccurate personal data and completion of incomplete data.",
      "exercise": "Request to the controller; free of charge; reply within 1 month (Art. 12).",
      "explicit": true,
      "quote": "The data subject shall have the right to obtain from the controller without undue delay the rectification of inaccurate personal data",
      "applies_from": "",
      "notes": ""
    }
  ]
}
```

Field rules:
- `entry_no`, `act` (short name): copy them from the index header (the table entry number) and the act's common short name.
- `article`: "Art. N" or "Art. N(p)" or "Art. N(p)(x)"; for proposals cite the proposal's numbering.
- `right`: short, standard name ("Right to lodge a complaint with a supervisory authority", "Right to choose a recommender option not based on profiling").
- `rightholder`: the person as the text names them (data subject, consumer, recipient of the service, end-user, person performing platform work, business user, rightholder, author, applicant, payment service user, injured person, any natural or legal person …).
- `holder_kind`: `"individual"` (natural persons only), `"any person"` (natural or legal persons), or `"organisation"` (only undertakings, legal persons, business users, organisations).
- `addressee`: the party who must honour it (controller, online platform provider, trader, gatekeeper, Member State/court, supervisory authority, Commission …).
- `category`: exactly one of:
  "Information & transparency" | "Access & copy" | "Rectification, erasure & restriction" | "Portability, switching & interoperability" |
  "Objection, opt-out, choice & consent" | "Human review & contesting decisions" | "Complaint (internal / out-of-court)" |
  "Complaint to authority" | "Judicial remedy & collective redress" | "Compensation & liability" |
  "Contractual remedies" | "Access to service & non-discrimination" | "Exclusive / IP rights & remuneration" |
  "Procedural rights" | "Data access & use" | "Other"
- `description`: one or two plain-English sentences on what the person can do or obtain.
- `exercise`: how, where, against whom, and key conditions or deadlines (short; "" if the text is silent).
- `explicit`: true if the text uses right/entitled/may-request-type language for the person; false if derived from another party's duty (like DSA 38).
- `quote`: verbatim excerpt (≤ 200 characters) copied exactly from the articles file. Never paraphrase it.
- `applies_from`: only if the article or act states a later application date for this right (e.g. "2026-08-02"); else "".
- `notes`: e.g. "Directive: exercised via national transposition law", "Only VLOPs/VLOSEs", "Proposal text; may change", "Member-State option".

Every assigned CELEX must appear in `sources`, even with 0 rights. Accuracy beats volume: no invented article numbers, and
check each article number against the file. Keep your final reply to the orchestrator short: the file path, rights per source,
and any problems (e.g. a garbled text file). Do not paste the JSON into your reply.
