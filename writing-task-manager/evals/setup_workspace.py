"""
Set up the eval workspace for writing-task-manager iteration 1.
Reads evals.json, creates per-eval directories with fixture files for
both with_skill and without_skill runs, and writes eval_metadata.json.
"""
import json
import os
from pathlib import Path

ROOT = Path("D:/Projects/ai-runtime-skills")
SKILL_PATH = ROOT / "writing-task-manager"
EVALS_PATH = SKILL_PATH / "evals" / "evals.json"
WORKSPACE = ROOT / "writing-task-manager-workspace"
ITERATION = WORKSPACE / "iteration-1"

# Read evals
with EVALS_PATH.open(encoding="utf-8") as f:
    data = json.load(f)

ITERATION.mkdir(parents=True, exist_ok=True)

# Slugify the eval name for the directory
def slug(name: str) -> str:
    return name.replace(" ", "-").lower()

for eval_def in data["evals"]:
    eval_id = eval_def["id"]
    eval_dir = ITERATION / f"eval-{eval_id}-{slug(eval_def['eval_name'])}"
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Write fixture files into both with_skill/ and without_skill/
    for run_kind in ("with_skill", "without_skill"):
        run_root = eval_dir / run_kind
        run_root.mkdir(exist_ok=True)
        for f in eval_def.get("files", []):
            target = run_root / f["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f["content"], encoding="utf-8")
        (run_root / "outputs").mkdir(exist_ok=True)

    # Write eval_metadata.json
    meta = {
        "eval_id": eval_id,
        "eval_name": eval_def["eval_name"],
        "prompt": eval_def["prompt"],
        "expected_output": eval_def["expected_output"],
        "assertions": [],
    }
    (eval_dir / "eval_metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"  set up eval-{eval_id}: {eval_dir.name}")

print(f"\nworkspace ready at: {ITERATION}")
print(f"  {len(data['evals'])} evals set up")
