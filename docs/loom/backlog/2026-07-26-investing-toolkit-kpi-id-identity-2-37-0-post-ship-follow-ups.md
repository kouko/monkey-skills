---
name: 2026-07-26-investing-toolkit-kpi-id-identity-2-37-0-post-ship-follow-ups
description: investing-toolkit kpi_id identity 2.37.0 — post-ship follow-ups
status: OPEN
---

- (a) 🟡 **No committed dogfood HARNESS.** The close-out dogfood (real
  `ingest_pack` → `kpi_store.append` over 47 cached live packs) is what caught the
  filename-length regression the 1084-test suite and the replay probe both missed —
  but it ran from a session scratchpad and was NOT committed, so the next arc has to
  rebuild it. The committed probe
  (`tests/data/fixtures/capture_kpi_id_identity_probe.py`) replays the selector loop
  only, by design. Making the dogfood repo-ready is real work (fetch/cache path,
  isolated stores, counts-only output) and wants its own test + review, which is why
  it was filed rather than patched in at close-out. Re-trigger: the next arc that
  changes a producer or the store's write path — per
  `docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`, do NOT let a probe
  stand in for it again.
- (a2) 🟡 **`_signature_key` and `derive_kpi_id` disagree about the
  ConsolidationItemsAxis — the guard can raise a FALSE collision.**
  `derive_kpi_id` EXCLUDES `srt:ConsolidationItemsAxis` from the breakdown pairs
  (`kpi_xbrl_ingest.py:255`); `_signature_key` leaves it in (`:348`). So a fact
  carrying that axis INSIDE `dimensions` — rather than in its own `consolidation`
  field — yields ONE kpi_id but TWO claim keys, and `_claim_kpi_id` refuses a pair
  the id derivation is explicitly tested to fold
  (`test_kpi_xbrl_ingest.py:662-669`). Executed probe, close-out review round 3:
  `{SegmentAxis: DataCenterMember, srt:ConsolidationItemsAxis: OperatingSegmentsMember}`
  + `consolidation=None` versus `{SegmentAxis: DataCenterMember}` +
  `consolidation="OperatingSegmentsMember"` → identical id, non-equal claim keys,
  raise. **Not reachable through the shipped producer**:
  `sec_edgar_client._dimension_signature` allowlists four breakdown axes and routes
  the consolidation axis to its own field (`:2265-2281`), so only a hand-built or
  third-party `--pack` can express it; and it fails LOUD (whole-pack abort), never a
  silent merge. Deliberately NOT fixed at close-out: aligning the two would change
  `_signature_key`'s selector grouping, a wider blast radius than the defect, and the
  brief scoped that function as untouched. Both affected docstrings now state the
  divergence instead of claiming unification. Re-trigger: any arc that admits
  third-party fact-packs, or the next touch of either key builder.
- (a3) 🟢 **Two modules disagree on what "the consolidation axes" means.**
  `kpi_xbrl_ingest._CONSOLIDATION_AXIS_LOCAL` (`:101`) names ONE axis; the producer's
  `sec_edgar_client._CONSOLIDATION_AXIS_LOCAL_NAMES` (`:1997-2000`) names TWO
  (`ConsolidationItemsAxis`, `ConsolidatedEntitiesAxis`) and folds both into the one
  `consolidation` field. Unreachable today for the same allowlist reason as (a2);
  fold into (a2)'s fix when it happens.
- (b) 🟢 **Predictable temp path in the probe capture script**
  (`tests/data/fixtures/capture_kpi_id_identity_probe.py:93`): the pack cache is a
  fixed name under the world-writable system temp dir (CWE-377), and its cached
  packs become committed evidence. Hand-run dev script only; move to `mkdtemp` or a
  repo-local ignored dir on next touch.
- (c) 🟢 **Stale cross-reference in the same script** (~:54-57): it cites "the
  sibling probe script's fetch loop", but the only committed sibling
  (`capture_companyconcept_form_domain.py`) has no fetch loop or cache. The
  reference does not resolve; fix wording on next touch.
