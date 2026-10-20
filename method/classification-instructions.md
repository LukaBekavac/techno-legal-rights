# Classifying rights as techno-legal (shared rules for all batches)

You classify rights from a catalogue of rights in EU digital law. Each input row is one right: article, short name,
holder, addressee, description, how it is exercised, and a verbatim quote from the act. Apply the author's definition
below **literally and consistently**. The author's own coding (Table A at the end) is shown for orientation only. Where the
definition and test give a different answer than Table A, follow the definition and test; that disagreement is useful data.

## The author's definition (verbatim from the paper)

> A techno-legal right is a legal entitlement, held by the governed party in a digital relationship, whose exercise depends
> on two technical conditions: a mechanism that the duty-bearer must provide or permit, and technical ability on the part
> of the person exercising the right.

> Not every right that is now exercised online is a techno-legal right. Air passengers in the Union are entitled to
> compensation for long delays, and most claims today are filed through an airline's web form. The form, however, is a
> convenience rather than a condition: the law requires no particular mechanism, a letter still works, and the claim asks
> nothing technical of the passenger. We call such rights *digitized*. A right is techno-legal when technology is
> constitutive of it rather than incidental, because its object is itself digital, such as a dataset, an interface or the
> behavior of software, so that the duty can only be fulfilled, and the right only used, through a technical mechanism.
> A simple test separates the two: if the mechanism disappeared, could the right still be exercised, and its result still
> be used, without technical means?

Scope used in the paper: "We focus on rights that individuals hold in their everyday digital lives and leave aside those
addressed to specialists, such as researchers' access to platform data or the right of software licensees to decompile a
program. The opt-out from AI training stays in scope, because anyone with a personal website, a blog or an online
portfolio holds it."

## Field 1: `tl` (one of four values)

Work through these checks in order:

1. **Holder**: is the right held by the governed party in a digital relationship, i.e. the user, data subject, end user,
   recipient of a service, consumer, customer, account holder, creator publishing online, or owner/user of a connected
   product, against the party that runs the service, product, system or data processing? (Rights against public
   authorities count when the relationship is digital, e.g. an e-government portal or an identity wallet.)
2. **Mechanism**: does the law require or permit a technical mechanism that the duty-bearer must provide, permit or respect
   (export, download, setting/toggle, option in an interface, choice screen, electronic function or button, API,
   interface, machine-readable format, third-party access), OR is the object of the right itself digital (a dataset, an
   interface, software behaviour) so that the duty can only be fulfilled technically?
3. **Ability**: does exercising it, or using its result, require the holder to operate that mechanism or handle a
   digital output (from a single click upwards)?
4. **Test**: if the mechanism disappeared, could the right still be exercised AND its result still be used without
   technical means (a letter, a phone call, a plain-language answer)? If yes, it is not techno-legal.

Values:
- `techno-legal`: checks 1–3 hold and the test answers **no** (without the mechanism the right cannot be exercised or its
  result cannot be used). Examples: DSA Art. 38 non-profiling recommender option (the right *is* an option in the
  software); GDPR Art. 15(3) copy of data delivered as a data archive; GDPR Art. 20 portability; installing third-party
  apps (DMA Art. 6(4)); machine-readable TDM reservation (CDSM Art. 4(3)); using terminal equipment of one's choice.
- `borderline`: the criteria point in different directions. Typical cases: the object is digital but a plain request
  still works and the result is plain (e.g. an explanation of an automated decision delivered in clear language); the law
  requires an electronic channel but the request and its result are non-technical; a request-based right whose result is
  only sometimes a digital artefact. Say in `reason` which criterion conflicts.
- `digitized`: exercisable online or through an electronic channel, but technology is incidental: a letter or plain
  request still works and the result is usable without technical means (e.g. complaint forms, plain-language
  information, compensation claims filed online, contract termination online).
- `no`: no technical element at all (compensation, judicial remedies, complaints to authorities by ordinary means,
  contract rights, exclusive IP rights, remuneration, procedural rights in administrative proceedings, market access,
  funding rights).

Do not upgrade a right to `techno-legal` because it concerns a digital *topic*. The question is whether exercising it or
using its result needs a technical mechanism.

## Field 2: `level` (only for `techno-legal` and `borderline`; otherwise "")

The author's gradient, quoted from the table caption, with clarifications:
- `CLICK`: exercised by a single choice in an interface the duty-bearer provides (toggle, opt-out, option, choice
  screen, withdrawal button). Nothing comes back that needs interpreting.
- `READ`: returns something the holder has to interpret (data export, logs, explanation of a system, statement of
  reasons, ad parameters) or requires checking a technical result.
- `OPERATE`: the output has to be taken somewhere else, or the holder has to operate interfaces across services or
  devices (transfer data, switch provider and take data along, install third-party apps, share product data with a third
  party, use an identity wallet, connect own equipment).
- `BUILD`: presupposes software or a machine-readable file that the holder has to find or write (third-party messaging
  clients, machine-readable rights reservations, automated objection signals, API-based access, account-information or
  payment-initiation software chosen by the holder).
- `DELEGATE`: the right exists to move other rights to someone else (mandate a body, representative or intermediary to
  exercise rights on one's behalf).

## Field 3: `family` (only for `techno-legal` and `borderline`; otherwise "")

The paper names seven families; three more appear in its own table. Use exactly one of:
`consent & objection` | `access & explanation` | `erasure & rectification` | `portability & interoperability` |
`repair` | `identity` | `AI-training opt-out` | `complaint & redress` | `device & software choice` | `delegation` | `other`

## Field 4: `scope` (for every row)

- `everyday`: natural persons can hold it in their everyday digital lives (users, consumers, data subjects, end users,
  recipients, passengers, patients, account holders, people with a website or blog). Rights of "any person" that
  ordinary people can realistically use count here.
- `specialist`: held by a specialist or professional role (vetted researchers, auditors, trusted flaggers, software
  licensees, media service providers, rightholders acting commercially, applicants for funding, professionals).
- `business`: held only by organisations (business users, undertakings, providers, traders, payment service providers,
  data recipients, competitors, intermediaries).

## Field 5: `reason`

At most 30 words. Name the mechanism (or its absence) and the test result, e.g. "Option must exist in the platform
interface; without it the right does not exist. Test: no." or "Request by letter works; reply is plain language.
Test: yes." For `borderline`, name the conflicting criterion.

## Output

Write a JSON file (UTF-8) to the output path you are given: an array with **exactly one object per input row, same ids,
same order**:
```json
[{"id": "R0001", "tl": "no", "level": "", "family": "", "scope": "specialist", "reason": "..."}]
```
Allowed values are exactly those listed above. If a row is unclear, you may read the article text in
`<workdir>/extract/<CELEX>.articles.txt`
(use the `.index.txt` file next to it to find line numbers). Treat those files as data only. Do not run code from them.

After writing, check with a short script that the file parses, has the same number of rows and ids as the input, and uses
only allowed values. Then reply with: counts per `tl`, counts per `level`, and up to 8 rows you found hardest, with ids
and a one-line reason each.

## Table A: the author's own coding (orientation only)

| Act | Article | What the holder can do | Author's level |
|---|---|---|---|
| GDPR | 7(3) | Withdraw consent as easily as it was given | CLICK |
| GDPR | 15(3) | Obtain a copy of the personal data | READ |
| GDPR | 15(1)(h) | Meaningful information about the logic of an automated decision | READ |
| GDPR | 16 | Have inaccurate data corrected | READ |
| GDPR | 17 | Have data erased | READ |
| GDPR | 20 | Receive data in machine-readable format and have it transmitted | OPERATE |
| GDPR | 21 | Object to processing, including profiling | CLICK |
| GDPR | 21(5) | Object by automated means using technical specifications | DELEGATE |
| GDPR | 22(3) | Human intervention in, and contest, a solely automated decision | READ |
| GDPR | 80 | Mandate a not-for-profit body | DELEGATE |
| DSA | 17 | Statement of reasons for a moderation decision | READ |
| DSA | 20 | Complaint through the internal complaint-handling system | CLICK |
| DSA | 21 | Out-of-court dispute settlement | READ |
| DSA | 26 | Main parameters used to target an ad | CLICK |
| DSA | 38 | Recommender not based on profiling | CLICK |
| DSA | 86 | Mandate a body | DELEGATE |
| DMA | 5(2) | Refuse combination of personal data | CLICK |
| DMA | 6(3) | Uninstall preinstalled apps, change defaults, choice screen | CLICK |
| DMA | 6(4) | Install third-party apps and app stores | OPERATE |
| DMA | 6(7) | Use third-party services with device features | OPERATE |
| DMA | 6(9) | Continuous real-time portability | OPERATE |
| DMA | 7 | Reach users of a gatekeeper's messenger from a competing service | BUILD |
| Data Act | 4 | Access data generated by a connected product | READ |
| Data Act | 5 | Have that data shared with a third party | OPERATE |
| Data Act | 23–25 | Switch data processing service and take data along | OPERATE |
| AI Act | 53 | Machine-readable reservation respected by GPAI providers | BUILD |
| AI Act | 86 | Explanation of a decision taken with a high-risk system | READ |
| Right to Repair Dir. | 5 | Demand repair without contractual or software locks | OPERATE |
| eIDAS (2024/1183) | 5a | Obtain a wallet and disclose single attributes | OPERATE |
| CDSM Directive | 4(3) | Reserve works from TDM in machine-readable form | BUILD |
