# Techno-legal rights in EU digital law

Data, legal texts and code for the paper *Techno-Legal Rights and Exercise Friction in EU Digital Law*
(Luka Bekavac, University of St. Gallen; under submission to ACM CS&Law 2027).

**Website:** <https://lukabekavac.github.io/techno-legal-rights/> lets you browse and filter every right.
[`#paper`](https://lukabekavac.github.io/techno-legal-rights/#paper) opens the twelve acts analysed in the paper.

## What is checked and what is not

| Data | Rights | Status |
|---|---|---|
| [`data/paper-12-acts/`](data/paper-12-acts) | 497 rights in the twelve acts analysed in the paper | **The data behind the paper.** Every right the model classified as techno-legal or borderline (169) was checked by the author against the legal text. |
| [`data/all-112-texts/`](data/all-112-texts) | 2,089 rights in 112 texts of EU digital law | Extracted and classified by the language model and checked automatically for quotes and article numbers. **Outside the twelve acts, nothing was checked by the author.** |

The twelve acts are:
- the GDPR, the Digital Services Act, the Digital Markets Act, the Data Act and the AI Act;
- the Consumer Rights Directive, the Digital Content Directive and the Cyber Resilience Act;
- the European Health Data Space Regulation and the Payment Services Directive;
- the European Digital Identity Regulation and the Directive on Copyright in the Digital Single Market.

Their 497 rights divide into:

| Class | Rights | By gradient level |
|---|---|---|
| techno-legal | 79 | 20 CLICK, 13 READ, 41 OPERATE, 5 BUILD |
| borderline | 90 | |
| digitized | 97 | |
| no technical element | 231 | |

The author changed the model's output in two places:
- Art. 53(1)(c) AI Act (`R1623`) is counted together with Art. 4(3) CDSM (`R1064`), to which it gives effect.
- Art. 7(7) DMA (`R0983`) moves to the family *portability & interoperability*.

## Contents

| Path | Content |
|---|---|
| `data/paper-12-acts/rights_12_acts.{json,csv}` | The paper's sample, with the two columns `author_checked` and `author_note` |
| `data/all-112-texts/rights_catalogue.{json,csv,xlsx}` | All rights. The spreadsheet adds a sheet per status group and a *Laws* sheet with a comment on each text |
| `data/all-112-texts/inventory.json` | The 104 entries of the source table and their status on 9 October 2026 |
| `laws/text/` | Plain text of the 147 documents downloaded, one file per CELEX number: the 112 texts analysed, plus 35 proposals and earlier versions that were not analysed |
| `laws/download_manifest.json` | Which version of each document was downloaded |
| `method/` | The written instructions given to the model for extraction and classification, verbatim except that local paths are shortened to `<workdir>/` |
| `scripts/` | The scripts for each step (Python 3; `openpyxl` for the spreadsheet) |
| `site/template.html`, `docs/index.html` | The website: its template and the built page, which is served by GitHub Pages |

## How the data was made

1. **Texts.** The starting point is Table 1 of J. Scott Marcus, Kamil Sekut and Kai Zenner,
   [*A Dataset on EU Legislation for the Digital World*](https://www.bruegel.org/sites/default/files/2023-07/Tables_Scott_Kai.pdf)
   (Bruegel, 2023), which has 104 entries. Their status was updated to 9 October 2026 (`inventory.py`). Which text was used:
   - for acts in force, the latest consolidated version;
   - for files in negotiation in 2023, the adopted act where there is one and otherwise the Commission proposal (withdrawn proposals are included and marked).

   This gives 112 texts.
2. **Download.** The texts were downloaded from Cellar, the repository of the EU Publications Office, and converted to plain text (`download.py`).
3. **Articles.** Each text was cut to its enacting terms and split into articles, with an index of keyword counts that told the model where to look (`articles.py`).
4. **Extraction.** Separate instances of the model, each given a group of acts, extracted every provision under which a person can actively invoke something ([`method/extraction-instructions.md`](method/extraction-instructions.md)). The four kinds were:
   - an express right;
   - an option built into another party's duty;
   - information owed to an identifiable person;
   - a remedy.

   This gave 2,089 rights in 101 texts. The other 11 texts confer none.
5. **Automatic checks.** Every quotation was found word for word in its act, and every cited article exists (`merge.py`).
6. **Classification.** Further instances of the model applied the paper's definition and test to every right ([`method/classification-instructions.md`](method/classification-instructions.md)). Each right got:
   - a class: techno-legal, borderline, digitized or no technical element;
   - a level on the gradient;
   - a family and a scope;
   - a short reason.

   A final pass changed 26 decisions where batches had treated like cases differently (`merge_tl.py`, `add_tl.py`).
7. **The author's check (paper sample only).** The author checked every techno-legal and borderline classification in the twelve acts against the legal text (`make_paper_subset.py`, which also asserts the paper's numbers).

Rebuild the sample and the website from the repository root:

```sh
python3 scripts/make_paper_subset.py
python3 scripts/build_site.py
```

## Use of a large language model

- **Model.** Claude Opus 5.5 (`claude-opus-5-5`, Anthropic), run through Claude Code between 9 and 11 October 2026.
- **What the model did.** Under the author's direction, it wrote and ran the scripts, extracted the rights (step 4) and classified them (step 6). It also built the website and helped draft this README.
- **What the author did.** The author chose the texts, set the rules and the examples, and checked every techno-legal and borderline classification in the twelve acts of the paper. No other right was checked by hand.
- **What was checked automatically.** The quotations and article numbers of all 2,089 rights.

Treat every classification outside the twelve acts as unverified model output.

## Fields

| Field | Meaning |
|---|---|
| `id`, `celex`, `act`, `article` | Identifier, CELEX number, short name of the act and the provision |
| `right`, `description`, `exercise`, `quote` | The right, what it gives, how it is exercised, and a quotation of at most 200 characters from the act |
| `rightholder`, `holder_kind`, `addressee` | Who holds it (individual / any person / organisation) and who owes it |
| `category`, `explicit` | Kind of right, and whether the text grants it expressly or through another party's duty |
| `in_effect_today`, `applies_from` | Whether it applies on 9 October 2026, and from when |
| `quote_verified`, `article_verified` | Results of the automatic checks |
| `techno_legal` | `techno-legal`, `borderline`, `digitized` or `no` |
| `tl_level`, `tl_family`, `tl_scope`, `tl_reason` | Gradient level, family, scope (`everyday`, `specialist`, `business`) and the model's reason |
| `paper_table2_level` | The author's earlier coding of 30 provisions (37 rows), which the classification instructions gave the model for orientation |

## Limits

- The data is not legal advice.
- Rights under directives reach people only through national transposition law, which was not analysed.
- Proposal texts may still change.
- Annexes were mostly not read.
- Some source texts have broken spacing (e.g. "provider s"), and quotations reproduce it exactly.

The legal texts are © European Union, <https://eur-lex.europa.eu>; their reuse is authorised under Commission Decision 2011/833/EU.

## Citation

Luka Bekavac. *Techno-Legal Rights and Exercise Friction in EU Digital Law.* Under submission, 2026.
