#!/usr/bin/env python3
"""Adversarial integrity checks for this one frozen experiment record."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRE_REBASE_BIRTH = "2aae5d8b4c1e3aaf5aac4f8c121af275f70abce2"
PRESERVED_BIRTH = "7a179e2c4d8ce7d651fd53cc5c8f4e5c201fbb17"
PRE_REBASE_BOUNDARY = "82b6adf798b4d3745242669b2885c0ee92a56869"
PRESERVED_BOUNDARY = "6b7b8b6c1fed2f7896421fef6f103f4a5934cd25"
BOUNDARY_PATCH_ID = "318d5c908216621a81a2e56e785a08f4a404cea9"
APPROVED_SHA256 = {
    "corpus-manifest.json": "6619f680c47fbc6cdcbbdc5fa3451c3eecfc8b2d1f538a7b5a4b2429f23a32a0",
    "input.txt": "0e9a021e6dbfceaa4103a79fa2c672fcdad344c18cf890c3a05b3cb6de39cf84",
    "prompt.txt": "e9b154b6cb1c71e060795b935b4fc1861d9bc5feab9c397f6f4ca60c9da8bb8d",
    "run-1.json": "12ee1d85550e48818a1a5d4557a7c94ccaa9009bc2e835895904995a6882b1d2",
    "run-2.json": "0e01c940ac75d6881b193fc7f7be5cc8712a9cc771e6315027f9dc15e4bf7aa9",
}
DOCUMENTS = {
    "technical": (
        "docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md",
        "6a6de5f298e991493bb141292b2715834a6dee5e",
        "2c39072425702cb8e0dc8e155a095672da1663fc6eb2eee0a9f23db4a96cc61e",
    ),
    "business": (
        "docs/loom/discovery/2026-08-31-docs-review-cost/business-value.md",
        "f874bf59c5a357f39f3edff50c6dec7cda33f4f5",
        "368cdcf750c44a1851b56e0a759605776ccc46b55382b2b3a75ac80992e3dda4",
    ),
    "strategy": (
        "docs/loom/discovery/2026-08-31-docs-review-cost/research/writer-versus-reviewer-attribution.md",
        "be0252e5ad4157d62befd0d96af5ed9c6507cd7f",
        "afd6005ce731f25939c55515d2f739259db90d40267bfd64141e85b7a62a28c7",
    ),
}


class VerificationError(RuntimeError):
    """A frozen evidence invariant did not hold."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load(root: Path, name: str) -> dict:
    return json.loads((root / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    require(completed.returncode == 0, f"git {' '.join(args)} failed")
    return completed.stdout


def repository_root() -> Path:
    return Path(git(ROOT, "rev-parse", "--show-toplevel").decode().strip())


def stable_patch_id(repo: Path, commit: str) -> str:
    patch = git(repo, "show", "--format=fuller", commit)
    return git(repo, "patch-id", "--stable", input_bytes=patch).decode().split()[0]


def verify_fixed_files(root: Path) -> None:
    for name, approved in APPROVED_SHA256.items():
        require(sha256(root / name) == approved, f"{name} differs from the approved record")


def verify_lineage(root: Path, repo: Path, manifest: dict) -> None:
    require(manifest["source_commit"] == PRE_REBASE_BIRTH, "source commit changed")
    require(manifest["boundary_commit"] == PRE_REBASE_BOUNDARY, "boundary commit changed")
    require(manifest["input_sha256"] == APPROVED_SHA256["input.txt"], "manifest input digest changed")
    require(manifest["prompt_sha256"] == APPROVED_SHA256["prompt.txt"], "manifest prompt digest changed")

    entries = {item["label"]: item for item in manifest["documents"]}
    require(set(entries) == set(DOCUMENTS), "corpus document population changed")
    for label, (path, blob, digest) in DOCUMENTS.items():
        expected = {"label": label, "path": path, "git_blob": blob, "sha256": digest}
        require(entries[label] == expected, f"{label} manifest entry changed")
        require(hashlib.sha256(git(repo, "cat-file", "blob", blob)).hexdigest() == digest, f"{label} blob digest changed")
        for birth in (PRE_REBASE_BIRTH, PRESERVED_BIRTH):
            resolved = git(repo, "rev-parse", f"{birth}:{path}").decode().strip()
            require(resolved == blob, f"{label} blob differs at {birth}")

    require(stable_patch_id(repo, PRE_REBASE_BOUNDARY) == BOUNDARY_PATCH_ID, "pre-rebase boundary patch changed")
    require(stable_patch_id(repo, PRESERVED_BOUNDARY) == BOUNDARY_PATCH_ID, "preserved boundary patch changed")
    provenance = (root / "provenance.md").read_text(encoding="utf-8")
    for identifier in (PRE_REBASE_BIRTH, PRESERVED_BIRTH, PRE_REBASE_BOUNDARY, PRESERVED_BOUNDARY, BOUNDARY_PATCH_ID):
        require(identifier in provenance, f"provenance omits {identifier}")


def verify_metrics(root: Path, oracle: dict, metrics: dict, runs: list[dict]) -> None:
    require([run["run_id"] for run in runs] == ["luna-repeat-1", "luna-repeat-2"], "run population changed")
    require(all(run["returncode"] == 0 for run in runs), "a replay did not succeed")
    require(all(run["requested_model"] == "gpt-5.6-luna" for run in runs), "requested model changed")

    expected = {item["id"] for item in oracle["expected_findings"]}
    require(expected == {"O1", "O2", "O3", "O4"}, "oracle population changed")
    require(all(item["origin"] == "initial-authoring" for item in oracle["expected_findings"]), "oracle origin changed")
    adjudication = oracle["adjudication"]
    matched = {run["run_id"]: set(adjudication[run["run_id"]]["matched"]) for run in runs}
    unmatched = {run["run_id"]: adjudication[run["run_id"]].get("unmatched_observations", []) for run in runs}
    require(adjudication["luna-repeat-1"]["unmatched_adjudication"] == "not adjudicated false", "unmatched observation was reclassified")

    valid_runs = sum(run["returncode"] == 0 for run in runs)
    observations = {run["run_id"]: len(run["raw_output"]["findings"]) for run in runs}
    matched_total = sum(len(items) for items in matched.values())
    unmatched_total = sum(len(items) for items in unmatched.values())
    opportunity_total = len(expected) * valid_runs
    observation_total = sum(observations.values())

    require(metrics["population"] == {
        "runs": len(runs), "documents_per_run": len(DOCUMENTS),
        "expected_findings_per_run": len(expected), "observations": observation_total,
        "valid_runs": valid_runs, "invalid_runs": len(runs) - valid_runs,
    }, "population metrics differ")
    require(metrics["finding_rate"] == {
        "numerator": matched_total, "denominator": opportunity_total,
        "value": matched_total / opportunity_total, "exclusions": [],
    }, "finding rate differs")
    require(metrics["unmatched_observation_rate"] == {
        "numerator": unmatched_total, "denominator": observation_total,
        "value": unmatched_total / observation_total, "exclusions": [],
        "adjudication": "not adjudicated false",
    }, "unmatched observation rate differs")

    intersection = len(matched["luna-repeat-1"] & matched["luna-repeat-2"])
    union = len(matched["luna-repeat-1"] | matched["luna-repeat-2"])
    require(metrics["repeat_agreement"] == {
        "formula": "Jaccard agreement over matched oracle IDs",
        "intersection": intersection, "union": union, "value": intersection / union,
    }, "repeat agreement differs")

    expected_per_run = {}
    for run in runs:
        run_id = run["run_id"]
        expected_per_run[run_id] = {
            "finding_rate": len(matched[run_id]) / len(expected),
            "unmatched_observation_rate": len(unmatched[run_id]) / observations[run_id],
            "observations": observations[run_id],
        }
    require(metrics["per_run"] == expected_per_run, "per-run metrics differ")

    expected_cost = {"elapsed_seconds_total": sum(run["elapsed_seconds"] for run in runs)}
    for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
        expected_cost[f"{key}_total"] = sum(run["usage"][key] for run in runs)
    require(set(metrics["cost"]) == set(expected_cost), "cost metric population changed")
    for key, value in expected_cost.items():
        if isinstance(value, float):
            require(math.isclose(metrics["cost"][key], value, rel_tol=0, abs_tol=1e-9), f"{key} differs")
        else:
            require(metrics["cost"][key] == value, f"{key} differs")


def verify_record(root: Path, repo: Path) -> None:
    verify_fixed_files(root)
    verify_lineage(root, repo, load(root, "corpus-manifest.json"))
    verify_metrics(root, load(root, "oracle.json"), load(root, "metrics.json"), [load(root, "run-1.json"), load(root, "run-2.json")])


def mutate_json(root: Path, name: str, mutate: Callable[[dict], None]) -> None:
    path = root / name
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    path.write_text(json.dumps(value), encoding="utf-8")


def expect_mutation_rejected(repo: Path, mutate: Callable[[Path], None], label: str) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        record = Path(temporary) / "evidence"
        shutil.copytree(ROOT, record, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(record)
        try:
            verify_record(record, repo)
        except VerificationError:
            return
        raise VerificationError(f"mutation was not rejected: {label}")


def run_mutation_cases(repo: Path) -> None:
    def coupled_input_manifest(root: Path) -> None:
        changed = (root / "input.txt").read_bytes() + b"\nchanged"
        (root / "input.txt").write_bytes(changed)
        mutate_json(root, "corpus-manifest.json", lambda value: value.__setitem__("input_sha256", hashlib.sha256(changed).hexdigest()))

    cases = {
        "coupled input and manifest": coupled_input_manifest,
        "published metric": lambda root: mutate_json(root, "metrics.json", lambda value: value["finding_rate"].__setitem__("value", 0.5)),
        "raw observation": lambda root: mutate_json(root, "run-1.json", lambda value: value["raw_output"]["findings"].pop()),
        "human adjudication": lambda root: mutate_json(root, "oracle.json", lambda value: value["adjudication"]["luna-repeat-1"].__setitem__("unmatched_adjudication", "false alarm")),
        "lineage mapping": lambda root: (root / "provenance.md").write_text((root / "provenance.md").read_text().replace(PRESERVED_BIRTH, "0" * 40), encoding="utf-8"),
    }
    for label, mutate in cases.items():
        expect_mutation_rejected(repo, mutate, label)


def main() -> None:
    repo = repository_root()
    verify_record(ROOT, repo)
    run_mutation_cases(repo)
    print("PASS: fixed evidence, complete metrics, lineage, and 5 mutations verified")


if __name__ == "__main__":
    main()
