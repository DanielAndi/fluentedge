# FluentEdge Dataset Card

## Current Functional Fixture

**Dataset name:** FluentEdge synthetic functional fixture<br>
**Release / version:** `synthetic-fixture-v1` / manifest `1.0.0`<br>
**Generated:** July 6, 2026<br>
**License:** No standalone public dataset license declared; limited to FluentEdge project testing<br>
**Source:** `tests/fixtures/generate_fixtures.py`<br>
**Locale / subset:** Synthetic English phrases; no real speaker locale<br>
**Clip count:** 48<br>
**Speaker groups:** 6 synthetic groups<br>
**Labels:** 24 `pass`, 24 `needs_review`<br>
**Manifest SHA-256:** `81b47ea142995e7cf6361c8f7e2b0272c78ba66ee94dc8f8393fd56a3b33408e`<br>
**Partition after Sprint 4 correction:** 32 train, 8 validation, 8 test clips with disjoint speaker groups

### Intended Use

The fixture tests schema validation, audio preprocessing, feature generation, candidate training, API inference, error handling, latency, concurrency, cleanup, and rollback wiring.

### Limitations

This is generated audio, not a sample of learners or natural speakers. It cannot support claims about pronunciation accuracy, generalization, accent fairness, subgroup performance, or production readiness. The perfect fixture macro F1 is functional evidence only.

## Required Public Validation Dataset

**Status:** Not acquired.<br>
**Candidate:** A licensed Mozilla Common Voice English subset or instructor-approved equivalent.<br>
**Blocker:** Dataset selection/download requires an explicit license decision and sufficient speaker metadata. No download or license acceptance is claimed.

Before model acceptance, record the exact release, source URL, accepted license, download date, locale, clip and speaker counts, total duration, manifest SHA-256, label derivation, exclusions, demographic limitations, and speaker-disjoint split results.
