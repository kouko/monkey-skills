"""Resolve historical evidence IDs through the committed extraction map."""
from pathlib import Path
import re


def migration_git_args(repo, args):
    map_path = Path(repo) / "docs/migration/commit-map.tsv"
    if not args or args[0] != "git" or not map_path.is_file():
        return args
    mapping = dict(line.split() for line in map_path.read_text().splitlines()[1:])
    result = []
    for argument in args:
        match = re.fullmatch(r"([0-9a-f]{7,40})([:^~].*)?", argument)
        if not match:
            result.append(argument)
            continue
        prefix, suffix = match.groups()
        candidates = [old for old in mapping if old.startswith(prefix)]
        if len(candidates) > 1:
            raise ValueError(f"ambiguous original revision: {prefix}")
        result.append(mapping[candidates[0]] + (suffix or "") if candidates else argument)
    return tuple(result)
