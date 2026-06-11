#!/usr/bin/env python3
"""skill-sync -- copy skill directories from this repo into each configured
agent's local skill directory.

Reads `mapping.json` next to this script. Syncs the skill directories listed
in `include_dirs` (each must exist under the repo root and contain a SKILL.md
whose frontmatter `name:` matches the directory name). For every enabled
agent, deletes the target skill dir if present and copies the source fresh,
skipping any subdirectory listed in `exclude_subdirs_in_skill` (e.g. `evals/`).

Stdlib only. Cross-platform.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MAPPING_PATH = SCRIPT_DIR / "mapping.json"
DEFAULT_REPO_ROOT = SCRIPT_DIR.parent


# ---------- Data model ----------

@dataclass(frozen=True)
class SyncOp:
    agent: str
    skill_name: str
    source: Path  # absolute
    target: Path  # absolute, resolved


# ---------- I/O helpers ----------

def _eprint(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)


# ---------- Frontmatter ----------

_NAME_RE = re.compile(
    r'''^name:\s*
        (?:
            "([^"\n]+)"                   # group 1: double-quoted
          | '([^'\n]+)'                   # group 2: single-quoted
          | ([A-Za-z0-9][A-Za-z0-9_-]*)   # group 3: bare
        )\s*$
    ''',
    re.MULTILINE | re.VERBOSE,
)
_FENCE_RE = re.compile(r"^---\s*$", re.MULTILINE)


def parse_skill_name(skill_md: Path) -> str | None:
    """Extract the `name:` field from SKILL.md's YAML frontmatter.

    Returns None if the file is missing, has no opening/closing `---` fences,
    or has no `name:` line in the frontmatter block.
    """
    try:
        text = skill_md.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    parts = _FENCE_RE.split(text, maxsplit=2)
    if len(parts) < 3:
        return None
    m = _NAME_RE.search(parts[1])
    if not m:
        return None
    # Three groups are mutually exclusive (alternation) -- exactly one is non-None.
    return m.group(1) or m.group(2) or m.group(3)


# ---------- Config ----------

def load_mapping(path: Path) -> dict:
    """Load and validate mapping.json. Fail-fast on any structural problem."""
    if not path.is_file():
        _eprint(f"[skill-sync] mapping.json not found: {path}")
        raise SystemExit(2)
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _eprint(f"[skill-sync] mapping.json is not valid JSON: {e}")
        raise SystemExit(2)

    if not isinstance(cfg, dict):
        _eprint("[skill-sync] mapping.json root must be an object")
        raise SystemExit(2)
    if cfg.get("version") != SCHEMA_VERSION:
        _eprint(
            f"[skill-sync] mapping.json version must be {SCHEMA_VERSION}, "
            f"got {cfg.get('version')!r}"
        )
        raise SystemExit(2)
    if not isinstance(cfg.get("agents"), dict) or not cfg["agents"]:
        _eprint("[skill-sync] mapping.json must define a non-empty `agents` object")
        raise SystemExit(2)
    if not isinstance(cfg.get("include_dirs"), list) or not cfg["include_dirs"]:
        _eprint("[skill-sync] mapping.json must define a non-empty `include_dirs` list")
        raise SystemExit(2)

    cfg.setdefault("exclude_subdirs_in_skill", [])
    return cfg


# ---------- Discovery ----------

def discover_skills(repo_root: Path, include_dirs: list[str]) -> list[Path]:
    """Return absolute paths to the skill directories listed in include_dirs.

    Each entry in include_dirs must:
      * point to an existing directory under repo_root
      * contain a SKILL.md
      * have a frontmatter `name:` that matches the directory name

    Entries failing any of these are skipped with a warning (other skills are
    still synced).
    """
    found: list[Path] = []
    for name in include_dirs:
        if not isinstance(name, str) or not name:
            _eprint(f"[skill-sync] WARN: include_dirs entry {name!r} is not a non-empty string -- skipping")
            continue
        # Reject path separators -- include_dirs lists names relative to the repo root, not nested paths.
        if "/" in name or "\\" in name or name in (".", ".."):
            _eprint(f"[skill-sync] WARN: include_dirs entry {name!r} must be a bare directory name -- skipping")
            continue
        skill_dir = repo_root / name
        if not skill_dir.is_dir():
            _eprint(f"[skill-sync] WARN: include_dirs entry {name!r} not found at {skill_dir} -- skipping")
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            _eprint(f"[skill-sync] WARN: {skill_md} not found -- skipping")
            continue
        fm_name = parse_skill_name(skill_md)
        if fm_name is None:
            _eprint(f"[skill-sync] WARN: {skill_md} has no parseable `name:` -- skipping")
            continue
        if fm_name != skill_dir.name:
            _eprint(
                f"[skill-sync] WARN: {skill_md} name={fm_name!r} != dir={skill_dir.name!r} -- skipping"
            )
            continue
        found.append(skill_dir.resolve())
    return found


# ---------- Path resolution ----------

def resolve_target(raw: str, repo_root: Path) -> Path:
    """Expand `~` and resolve relative paths against repo_root."""
    # Normalize trailing slashes so "./.kilo/skills/" and "./.kilo/skills" agree.
    raw = raw.rstrip("/\\") or raw
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = repo_root / p
    return p.resolve()


# ---------- Transfer ----------

def _ignore_factory(exclude_subdirs: set[str]):
    """shutil.copytree `ignore` callback that drops any subdir whose basename
    is in exclude_subdirs, at any depth."""
    def _ignore(dirpath, names):
        return [n for n in names if n in exclude_subdirs]
    return _ignore


def sync_skill(
    op: SyncOp,
    exclude_subdirs: set[str],
    dry_run: bool,
    quiet: bool,
) -> tuple[bool, str]:
    """Replace op.target with a fresh copy of op.source, skipping excluded
    subdirs. Returns (ok, message)."""
    label = f"[{op.agent}] {op.skill_name:<24}"
    arrow = f"-> {op.target}"

    if dry_run:
        action = "would replace" if op.target.exists() else "would create"
        if not quiet:
            print(f"{label} {action} {arrow}")
        return True, "dry-run"

    try:
        if op.target.exists():
            if op.target.is_symlink() or op.target.is_file():
                op.target.unlink()
            else:
                shutil.rmtree(op.target)
        op.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            op.source,
            op.target,
            ignore=_ignore_factory(exclude_subdirs),
            symlinks=False,
        )
    except OSError as e:
        msg = f"FAILED ({e.__class__.__name__}: {e})"
        _eprint(f"{label} {msg}")
        return False, msg

    if not quiet:
        excluded = sorted(exclude_subdirs & {p.name for p in op.source.iterdir() if p.is_dir()})
        suffix = f"  (excluded: {', '.join(excluded)})" if excluded else ""
        print(f"{label} synced {arrow}{suffix}")
    return True, "ok"


# ---------- Orchestration ----------

def plan_ops(
    agents: dict,
    skills: list[Path],
    repo_root: Path,
) -> list[SyncOp]:
    """Build the cartesian product of agents x skills with resolved targets.

    With the include_dirs model, only the dirs the user explicitly listed get
    discovered, so the in-repo recursion risk is much smaller. The remaining
    failure modes worth guarding:
      * target equals repo_root  -> would map source skill onto itself
      * target equals one of the source skill dirs  -> would nest source/source
    Both are refused with a warning; other ops still run.
    """
    skill_paths = {s.resolve() for s in skills}
    ops: list[SyncOp] = []
    for agent_name, agent_cfg in agents.items():
        target_dir = resolve_target(agent_cfg["target"], repo_root)

        if target_dir == repo_root:
            _eprint(
                f"[skill-sync] WARN: agent {agent_name!r} target is the repo root "
                f"({target_dir}) -- would overwrite source skills; skipping"
            )
            continue
        if target_dir in skill_paths:
            _eprint(
                f"[skill-sync] WARN: agent {agent_name!r} target {target_dir} "
                f"is a source skill dir; skipping"
            )
            continue

        if target_dir.exists() and target_dir.is_file():
            _eprint(
                f"[skill-sync] ERROR: agent {agent_name!r} target {target_dir} "
                f"is a file, expected a directory"
            )
            raise SystemExit(2)

        for skill in skills:
            ops.append(
                SyncOp(
                    agent=agent_name,
                    skill_name=skill.name,
                    source=skill,
                    target=target_dir / skill.name,
                )
            )
    return ops


def _filter_agents(agents: dict, only: list[str] | None) -> dict:
    """Drop disabled agents, then apply --agent filter (fail-fast on typos)."""
    enabled = {n: c for n, c in agents.items() if c.get("enabled", True)}
    if only is None:
        return enabled
    unknown = [n for n in only if n not in agents]
    if unknown:
        _eprint(
            f"[skill-sync] ERROR: unknown agent(s) {unknown}. "
            f"Known: {sorted(agents)}"
        )
        raise SystemExit(2)
    return {n: c for n, c in enabled.items() if n in only}


def _filter_skills(skills: list[Path], only: list[str] | None) -> list[Path]:
    """Apply --skill filter (fail-fast on typos)."""
    if only is None:
        return skills
    by_name = {p.name: p for p in skills}
    unknown = [n for n in only if n not in by_name]
    if unknown:
        _eprint(
            f"[skill-sync] ERROR: unknown skill(s) {unknown}. "
            f"Discovered: {sorted(by_name)}"
        )
        raise SystemExit(2)
    return [by_name[n] for n in only]


# ---------- Main ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-sync",
        description="Sync skills from this repo into each agent's skill directory.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen; perform no IO.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-operation lines (summary still prints).")
    parser.add_argument("--agent", action="append", default=None, metavar="NAME",
                        help="Restrict to this agent. Repeatable.")
    parser.add_argument("--skill", action="append", default=None, metavar="NAME",
                        help="Restrict to this skill. Repeatable.")
    parser.add_argument("--repo-root", type=Path, default=None, metavar="PATH",
                        help="Override repo root (default: parent of script dir).")
    parser.add_argument("--mapping", type=Path, default=None, metavar="PATH",
                        help="Override mapping.json path.")
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or DEFAULT_REPO_ROOT).resolve()
    if not repo_root.is_dir():
        _eprint(f"[skill-sync] repo root not found: {repo_root}")
        return 2

    mapping_path = (args.mapping or DEFAULT_MAPPING_PATH).resolve()
    cfg = load_mapping(mapping_path)
    include_dirs = cfg["include_dirs"]
    exclude_subdirs = set(cfg["exclude_subdirs_in_skill"])

    skills = discover_skills(repo_root, include_dirs)
    if not skills:
        print(f"[skill-sync] No skills found in {repo_root}. Nothing to do.")
        return 0

    skills = _filter_skills(skills, args.skill)
    agents = _filter_agents(cfg["agents"], args.agent)
    if not agents:
        print("[skill-sync] No enabled agents (after filtering). Nothing to do.")
        return 0

    ops = plan_ops(agents, skills, repo_root)
    if not ops:
        print("[skill-sync] No sync operations planned. Nothing to do.")
        return 0

    if not args.quiet:
        print(f"[skill-sync] repo: {repo_root}")
        print(f"[skill-sync] discovered {len(skills)} skill(s): "
              f"{', '.join(p.name for p in skills)}")
        print(f"[skill-sync] {len(agents)} agent(s) enabled: "
              f"{', '.join(agents)}")
        if args.dry_run:
            print("[skill-sync] (dry-run -- no files will be written)")
        print()

    failures = 0
    for op in ops:
        ok, _ = sync_skill(op, exclude_subdirs, args.dry_run, args.quiet)
        if not ok:
            failures += 1

    print()
    verb = "Would sync" if args.dry_run else "Synced"
    print(
        f"[skill-sync] {verb} {len(skills)} skill(s) to {len(agents)} agent(s) "
        f"({len(ops)} operations, {failures} failure(s))"
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
