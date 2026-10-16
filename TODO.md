# TODO

## Unverified companies (partly done)

Done:
- Removed duplicate entries (Hootsuite, Redbrick) from `companies.yaml`; 54 companies remain.
- Re-ran `detect_ats.py`: 14 of 54 verified, the rest `active: false` in `companies_verified.yaml`.
- Recorded why in a `note:` field where we found out (acquired, or on an ATS we have no adapter for).

Still open:
- **Missing adapters** for ATS platforms real targets use: Teamtailor and Jobvite (KIXEYE),
  Recruitee (VertiGIS), BambooHR (Niricson), Kula (Dapper Labs), plus Workday and custom
  sites (Fortinet, SAP, Amazon, Microsoft, EA). Worth building only if those companies matter.
- **~25 small companies with no discoverable board.** Guessing slug variants on the four
  supported ATSs found nothing (two hits were other companies with similar names). Their careers
  pages are JS-rendered or block bots, so the right board has to be found by hand: open each
  careers page in a browser and look at where "Apply" links point.
  Candidates: Certn, Redbrick, Dyspatch, MarineLabs, Clio, Vecima, Reliable Controls, Rooof,
  AggregateIQ, Animikii, Flytographer, Pani Energy, Checkfront, Tutela, Hololabs, Opn Media,
  Blue Wizard Digital, Codename Entertainment, Stocksy, BRNKL, Open Ocean Robotics, Plurilock,
  Worldline, Invoke Solutions, Glowforge, Ballard, Tiny.
- Once a board is found, fix `ats`/`slug` in `companies.yaml`, set `active: true`, and re-run
  `python ingestion/detect_ats.py`.
