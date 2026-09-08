"""W0-01 — loom-code contract package: manifest.yaml is the machine-readable
declaration of stations / tools / actions / artifact schemas (concept-model
§1, §2, §3, §11). Every station and artifact named anywhere in the loom
family must resolve here; mechanisms.yaml (W0-06) recomputes from it."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "loom-code" / "contract"
MANIFEST = CONTRACT / "manifest.yaml"
TEMPLATES = CONTRACT / "templates"

STATIONS = {
    "capture-intent": "loom-design",
    "write-spec": "loom-design",
    "write-plan": "loom-code",
    "build": "loom-code",
    "review": "loom-code",
    "ship": "loom-code",
    "maintain": "loom-code",
}
ARTIFACTS = {
    "intent", "spec", "plan", "review", "attestation",
    "blind-run-report", "memory", "kickoff-defaults",
}
# The four W0-01 additions declare no `fields:` schema of their own (their
# content is free-form prose / an existing sub-key of review.json, not a
# frontmatter/section/json-key schema) and two of them (blind-run-report,
# blind-run-report has no template file -- it is a per-change artifact
# charter rows, not new template-backed schemas.
ARTIFACTS_WITHOUT_FIELDS_SCHEMA = {"blind-run-report", "memory", "kickoff-defaults", "dispatch"}
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_parses_and_is_versioned(manifest):
    assert re.fullmatch(r"\d+\.\d+\.\d+", str(manifest["version"]))


def test_seven_stations_with_owner(manifest):
    got = {s["name"]: s["owner"] for s in manifest["stations"]}
    assert got == STATIONS
    for s in manifest["stations"]:
        assert s["produces"] in ARTIFACTS | {"diff"}, s["name"]


def test_loom_code_station_names_match_skill_dirs(manifest):
    """The manifest's loom-code stations ARE the skills/ directory listing —
    no exemption list any more: W1-06 deleted the pre-redesign directories,
    so a directory that is not a declared station is a defect, not a
    leftover."""
    declared = {s["name"] for s in manifest["stations"] if s["owner"] == "loom-code"}
    on_disk = {p.name for p in (REPO / "loom-code" / "skills").iterdir() if p.is_dir()}
    assert declared == on_disk


def test_every_action_names_one_owner_station(manifest):
    names = set(STATIONS)
    for a in manifest["actions"]:
        assert ID_RE.match(a["name"]), a
        assert a["owner"] in names, a
        assert a.get("summary"), a


def test_artifact_schemas_declare_fields_and_templates(manifest):
    schemas = manifest["artifacts"]
    assert set(schemas) == ARTIFACTS
    for name, schema in schemas.items():
        assert schema["path"], name
        if name in ARTIFACTS_WITHOUT_FIELDS_SCHEMA:
            assert schema.get("fields", []) == [], name
            if schema.get("template") is not None:
                tmpl = TEMPLATES / schema["template"]
                assert tmpl.is_file(), f"{name}: template missing {tmpl}"
            continue
        assert isinstance(schema["fields"], list) and schema["fields"], name
        tmpl = TEMPLATES / schema["template"]
        assert tmpl.is_file(), f"{name}: template missing {tmpl}"


def test_markdown_templates_carry_declared_fields(manifest):
    """Every frontmatter field / section the schema declares appears in the
    template, so the template and the schema cannot drift apart. Skips an
    artifact with no template file at all (`template: null` -- W0-01's
    blind-run-report and dispatch, which are prose / a review.json sub-key,
    not a template-backed schema)."""
    for name, schema in manifest["artifacts"].items():
        if schema.get("template") is None:
            continue
        tmpl = (TEMPLATES / schema["template"]).read_text(encoding="utf-8")
        for f in schema.get("fields", []):
            key = f["name"]
            assert key in tmpl, f"{name}: field {key!r} not in template {schema['template']}"


def test_dispatch_is_not_part_of_generated_attestation(manifest):
    """Process accounting is not publication evidence."""
    assert "review-dispatch" not in manifest["artifacts"]
    names = [f["name"] for f in manifest["artifacts"]["attestation"]["fields"]]
    assert "dispatch" not in names
    assert not (TEMPLATES / "review-dispatch.json").exists()
    assert "review.json.dispatch" not in MANIFEST.read_text(encoding="utf-8")


def test_tools_count_and_owner(manifest):
    tools = manifest["tools"]
    counted = [t for t in tools if not t.get("standalone")]
    assert len(counted) == 10  # 8 loom-workflow + 2 loom-design; 7 stations + 10 = 17 ≤ 18
    assert {t["name"] for t in tools if t.get("standalone")} == {"goal-create", "dbt-model-style"}
    assert {t["owner"] for t in tools} <= {"loom-design", "loom-workflow"}


def test_kickoff_defaults_keys_declared(manifest):
    keys = {k["name"] for k in manifest["kickoff_defaults"]}
    assert {"second-vendor", "standing-docs", "session-start-baseline",
            "interface-surfaces", "artifact-types"} <= keys


def test_manifest_declares_publication_only_paths(manifest):
    patterns = manifest["publication_only_paths"]
    assert patterns == ["docs/loom/<change-id>/attestation.json"]


def test_manifest_declares_generated_attestation(manifest):
    schema = manifest["artifacts"]["attestation"]
    assert schema["path"] == "docs/loom/<change-id>/attestation.json"
    assert schema["template"] == "attestation.json"
    names = [field["name"] for field in schema["fields"]]
    assert names == ["schema", "change_id", "content_digest", "executions", "verdicts", "findings"]
    assert manifest["artifacts"]["review"]["charter"]["readers"] == ["write-plan"]
