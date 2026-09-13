from __future__ import annotations

from loom_checker.helpers import UsageError
import re


REQUIRED_VERSION = re.compile(r"(\d+)\.(\d+)")


def parse_required_version(required: str):
    wanted = REQUIRED_VERSION.fullmatch(required.strip())
    if not wanted:
        raise UsageError(f"`--require {required}` is not <major>.<minor>.")
    return wanted


def check_contract_requires(version: str, required: str) -> list[tuple[str, str]]:
    wanted = parse_required_version(required)

    shipped = REQUIRED_VERSION.match(version)
    if not shipped:
        raise UsageError(f"the contract manifest declares no readable version ({version!r}).")

    same_major = shipped.group(1) == wanted.group(1)
    if same_major and int(shipped.group(2)) >= int(wanted.group(2)):
        return []
    if int(wanted.group(1)) < int(shipped.group(1)):
        # This repo's contract has already moved past the required major --
        # the consuming plugin is what is stale, not loom-code.
        reason = (
            f"this repo ships loom contract {version}, but the consuming plugin "
            f"declares an old contract major (--require {required}); update that "
            "plugin's requires-contract to a supported major."
        )
    else:
        # Either the required major is higher than shipped, or the major
        # matches but the minor floor isn't met -- either way loom-code
        # itself is what needs updating.
        reason = (
            f"this repo ships loom contract {version}, but >={required} is "
            "required — 請更新 loom-code。"
        )
    return [("contract.requires", reason)]
