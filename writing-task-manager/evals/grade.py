"""
Grade the eval runs. For each eval, apply the assertions to both
with_skill/ and without_skill/ outputs and write grading.json.

Assertions are objectively verifiable file-content checks. Each gets
a descriptive name, the check logic, and the resulting {text, passed, evidence}.
"""
import json
import re
from pathlib import Path

ITERATION = Path("D:/Projects/ai-runtime-skills/writing-task-manager-workspace/iteration-1")

# Each assertion is: (name, check_fn) where check_fn(run_dir) -> (passed: bool, evidence: str)
# run_dir is the with_skill/ or without_skill/ subdirectory of an eval.

def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

def has_lines_matching(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.MULTILINE))

# ---------------- Eval 1: cold-start record single file ----------------
def eval1_assertions(run: Path):
    wt = run / ".writing-tasks"
    idx = wt / "writing-task-manager.md"
    tf = wt / "resume.md"
    out = []
    out.append((
        "storage_dir_created",
        (wt.exists() and wt.is_dir(),
         f".writing-tasks/ exists: {wt.exists()}; is_dir: {wt.exists() and wt.is_dir()}"),
    ))
    out.append((
        "index_file_created",
        (idx.exists(),
         f".writing-tasks/writing-task-manager.md exists: {idx.exists()}"),
    ))
    idx_text = read(idx)
    out.append((
        "index_has_header",
        (idx_text.startswith("# Writing tasks"),
         f"index starts with '# Writing tasks': {idx_text.startswith('# Writing tasks')!r}"),
    ))
    out.append((
        "task_file_created",
        (tf.exists(),
         f".writing-tasks/resume.md exists: {tf.exists()}"),
    ))
    tf_text = read(tf)
    task_lines = [l for l in tf_text.splitlines() if re.match(r"^\s*-\s*\[", l)]
    out.append((
        "task_file_has_three_lines",
        (len(task_lines) == 3,
         f"task-line count = {len(task_lines)}; lines = {task_lines!r}"),
    ))
    all_unfinished = all(re.match(r"^\s*-\s*\[\s*\]", l) for l in task_lines)
    out.append((
        "all_tasks_unfinished",
        (all_unfinished,
         f"all task lines are - [ ]: {all_unfinished}; lines = {task_lines!r}"),
    ))
    out.append((
        "index_has_resume_line",
        (bool(re.search(r"resume\.md", idx_text)),
         f"index mentions resume.md: {bool(re.search(r'resum\\.md', idx_text))}; content = {idx_text!r}"),
    ))
    descs = [re.sub(r"^\s*-\s*\[\s*\]\s*", "", l).strip() for l in task_lines]
    expected_descs = [
        "Add a summary section at the top",
        "Fix the dates in the experience section (they're wrong on the second job)",
        "Add my new GitHub URL",
    ]
    missing = [d for d in expected_descs if d not in descs]
    out.append((
        "user_wording_preserved",
        (len(missing) == 0,
         f"missing expected descriptions: {missing!r}; got: {descs!r}"),
    ))
    return out

# ---------------- Eval 2: check mode with partials ----------------
def eval2_assertions(run: Path):
    idx = run / ".writing-tasks/writing-task-manager.md"
    methods = run / ".writing-tasks/chapters/methods.md"
    intro = run / ".writing-tasks/intro.md"
    chat = read(run / "outputs/chat_response.md")
    out = []
    expected_idx = "# Writing tasks\n\n- [ ] ./chapters/methods.md\n- [ ] ./intro.md\n"
    expected_methods = "- [ ] Rewrite the sampling paragraph for clarity\n- [~] Add the new citation from Smith 2024\n- [x] Fix typo in the section heading\n"
    expected_intro = "- [ ] Add thesis statement\n- [ ] Proofread final paragraph\n"
    out.append((
        "index_unchanged",
        (read(idx) == expected_idx,
         f"index matches expected pre-existing content: {read(idx) == expected_idx}"),
    ))
    out.append((
        "methods_task_unchanged",
        (read(methods) == expected_methods,
         f"chapters/methods.md unchanged: {read(methods) == expected_methods}"),
    ))
    out.append((
        "intro_task_unchanged",
        (read(intro) == expected_intro,
         f"intro.md unchanged: {read(intro) == expected_intro}"),
    ))
    out.append((
        "partial_surfaced_in_chat",
        ("Add the new citation from Smith 2024" in chat and ("partial" in chat.lower() or "[~]" in chat),
         f"chat mentions the partial task and 'partial'/[~] term: 'Add the new citation from Smith 2024' in chat = {'Add the new citation from Smith 2024' in chat}; 'partial' in chat = {'partial' in chat.lower()}; '[~]' in chat = {'[~]' in chat}"),
    ))
    out.append((
        "open_work_listed",
        ("chapters/methods.md" in chat and "intro.md" in chat,
         f"chat mentions both files: methods = {'chapters/methods.md' in chat}; intro = {'intro.md' in chat}"),
    ))
    out.append((
        "uses_skill_storage_paths",
        (".writing-tasks" in chat or "writing-task-manager.md" in chat,
         f"chat references skill storage paths: .writing-tasks = {'.writing-tasks' in chat}; writing-task-manager.md = {'writing-task-manager.md' in chat}"),
    ))
    return out

# ---------------- Eval 3: mark finished removes from index ----------------
def eval3_assertions(run: Path):
    idx = run / ".writing-tasks/writing-task-manager.md"
    tf = run / ".writing-tasks/resume.md"
    out = []
    tf_text = read(tf)
    out.append((
        "task_marked_done",
        (bool(re.search(r"^\s*-\s*\[x\]\s*Add a summary section", tf_text, re.MULTILINE)),
         f"- [x] Add a summary section found: {bool(re.search(r'^\\s*-\\s*\\[x\\]\\s*Add a summary section', tf_text, re.MULTILINE))}; task file = {tf_text!r}"),
    ))
    idx_text = read(idx)
    out.append((
        "index_line_removed",
        ("resume.md" not in idx_text,
         f"index does not contain 'resume.md': {'resume.md' not in idx_text}; content = {idx_text!r}"),
    ))
    out.append((
        "index_header_preserved",
        (idx_text.startswith("# Writing tasks"),
         f"index still starts with '# Writing tasks': {idx_text.startswith('# Writing tasks')}; content = {idx_text!r}"),
    ))
    return out

# ---------------- Eval 4: add with dedup ----------------
def eval4_assertions(run: Path):
    tf = run / ".writing-tasks/resume.md"
    out = []
    tf_text = read(tf)
    out.append((
        "new_task_added",
        (bool(re.search(r"^\s*-\s*\[\s*\]\s*rewrite the experience section", tf_text, re.MULTILINE)),
         f"- [ ] rewrite the experience section found: {bool(re.search(r'^\\s*-\\s*\\[\\s*\\]\\s*rewrite the experience section', tf_text, re.MULTILINE))}"),
    ))
    summary_count = len(re.findall(r"^\s*-\s*\[.\]\s*Add a summary section", tf_text, re.MULTILINE))
    out.append((
        "no_duplicate_summary_task",
        (summary_count == 1,
         f"'Add a summary section' line count = {summary_count} (expected 1)"),
    ))
    task_lines = [l for l in tf_text.splitlines() if re.match(r"^\s*-\s*\[", l)]
    out.append((
        "task_file_has_three_lines",
        (len(task_lines) == 3,
         f"task-line count = {len(task_lines)} (expected 3); lines = {task_lines!r}"),
    ))
    return out

EVALS = [
    (1, "cold-start-record-single-file", eval1_assertions),
    (2, "check-mode-with-partials", eval2_assertions),
    (3, "mark-finished-removes-from-index", eval3_assertions),
    (4, "add-with-dedup", eval4_assertions),
]

results_summary = []

for eval_id, slug, assertion_fn in EVALS:
    eval_dir = ITERATION / f"eval-{eval_id}-{slug}"
    for run_kind in ("with_skill", "without_skill"):
        run_dir = eval_dir / run_kind
        checks = assertion_fn(run_dir)
        grading = {"assertions": []}
        for name, (passed, evidence) in checks:
            grading["assertions"].append({
                "text": name,
                "passed": bool(passed),
                "evidence": evidence,
            })
        out_path = run_dir / "grading.json"
        out_path.write_text(json.dumps(grading, indent=2, ensure_ascii=False), encoding="utf-8")
        n_pass = sum(1 for a in grading["assertions"] if a["passed"])
        n_total = len(grading["assertions"])
        results_summary.append((eval_id, slug, run_kind, n_pass, n_total))
        print(f"  {slug} / {run_kind}: {n_pass}/{n_total} passed")

# Benchmark aggregation
benchmark = {
    "skill_name": "writing-task-manager",
    "iteration": 1,
    "evals": [],
}
for eval_id, slug, _, _n_pass, _n_total in [(e, s, None, 0, 0) for e, s, _ in EVALS]:
    eval_dir = ITERATION / f"eval-{eval_id}-{slug}"
    eval_results = {
        "eval_id": eval_id,
        "eval_name": slug,
        "with_skill": {},
        "without_skill": {},
    }
    for run_kind in ("with_skill", "without_skill"):
        g = json.loads((eval_dir / run_kind / "grading.json").read_text(encoding="utf-8"))
        n_pass = sum(1 for a in g["assertions"] if a["passed"])
        n_total = len(g["assertions"])
        eval_results[run_kind] = {
            "pass_rate": n_pass / n_total if n_total else 0,
            "passed": n_pass,
            "total": n_total,
            "assertions": g["assertions"],
        }
    benchmark["evals"].append(eval_results)

# Per-config summary
for run_kind in ("with_skill", "without_skill"):
    total_pass = sum(e[run_kind]["passed"] for e in benchmark["evals"])
    total_n = sum(e[run_kind]["total"] for e in benchmark["evals"])
    benchmark[f"{run_kind}_pass_rate"] = total_pass / total_n if total_n else 0
    benchmark[f"{run_kind}_passed"] = total_pass
    benchmark[f"{run_kind}_total"] = total_n

(ITERATION / "benchmark.json").write_text(
    json.dumps(benchmark, indent=2, ensure_ascii=False), encoding="utf-8"
)

# Pretty-print a markdown summary too
lines = ["# Benchmark — writing-task-manager — iteration 1\n"]
lines.append(f"- **with_skill**: {benchmark['with_skill_passed']}/{benchmark['with_skill_total']} assertions passed ({benchmark['with_skill_pass_rate']*100:.0f}%)")
lines.append(f"- **without_skill**: {benchmark['without_skill_passed']}/{benchmark['without_skill_total']} assertions passed ({benchmark['without_skill_pass_rate']*100:.0f}%)\n")
lines.append("| Eval | with_skill | without_skill |")
lines.append("|------|------------|---------------|")
for e in benchmark["evals"]:
    w = f"{e['with_skill']['passed']}/{e['with_skill']['total']}"
    b = f"{e['without_skill']['passed']}/{e['without_skill']['total']}"
    lines.append(f"| {e['eval_name']} | {w} | {b} |")
lines.append("")
(ITERATION / "benchmark.md").write_text("\n".join(lines), encoding="utf-8")

print("\nWrote benchmark.json and benchmark.md")
