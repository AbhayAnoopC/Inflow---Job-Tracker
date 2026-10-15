# TODO

## Fix unverified company slugs (revisit after the MVP is working)

`ingestion/detect_ats.py` verified only 15 of 56 companies; the other 41 are
`active: false` in `companies_verified.yaml` and are skipped by the pipeline.

- Look up the correct ATS/slug for the large unverified companies (Clio, Fortinet,
  Dapper Labs, Bench, KIXEYE, Copperleaf, Ballard, Certn, Redbrick, ...). Some may be on
  Workday or a custom careers site (no adapter yet), some may simply have 0 open jobs today.
- Remove duplicate entries in `companies.yaml` (Hootsuite x2, Redbrick x2).
- Re-run `python ingestion/detect_ats.py` and commit the refreshed `companies_verified.yaml`.
