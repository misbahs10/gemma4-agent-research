from pathlib import Path
from datetime import datetime
import json
import shutil

ROOT = Path.cwd()
metadata_path = ROOT / "benchmark/metadata/repositories.json"
tasks_path = ROOT / "benchmark/tasks/benchmark_tasks.json"
repo_path = ROOT / "data/raw/order_app_repo"

required_repo_files = [
    "main.py",
    "order_service.py",
    "pricing.py",
    "discounts.py",
]

for filename in required_repo_files:
    if not (repo_path / filename).is_file():
        raise FileNotFoundError(f"Missing repository file: {repo_path / filename}")

metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
benchmark = json.loads(tasks_path.read_text(encoding="utf-8-sig"))

original_tasks = benchmark["tasks"]
original_task_count = len(original_tasks)

if original_task_count != 10:
    raise RuntimeError(
        f"Expected 10 original tasks, found {original_task_count}. "
        "No changes made."
    )

if any(r["repository_id"] == "repo002" for r in metadata["repositories"]):
    raise RuntimeError("repo002 is already registered. No changes made.")

if any(t["repository_id"] == "repo002" for t in original_tasks):
    raise RuntimeError("repo002 tasks already exist. No changes made.")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = ROOT / "results/backups" / f"benchmark_expansion_{timestamp}"
backup_dir.mkdir(parents=True, exist_ok=False)

files_to_backup = [
    metadata_path,
    tasks_path,
    ROOT / "results/logs/multi_repository_results.json",
    ROOT / "results/metrics/multi_repository_comparison.csv",
    ROOT / "results/metrics/multi_repository_summary.csv",
]

for source in files_to_backup:
    if source.is_file():
        shutil.copy2(source, backup_dir / source.name)

print(f"Backups saved to: {backup_dir}")

new_repository = {
    "repository_id": "repo002",
    "name": "order_app_repo",
    "path": "data/raw/order_app_repo",
    "language": "python",
    "source": "local_development_repository",
    "purpose": "Multi-file order processing, pricing, and discount call-chain evaluation"
}

tasks_to_add = [
    {
        "task_id": "repo002_task001",
        "repository_id": "repo002",
        "task_type": "symbol_localization",
        "task": "Find where the create_order function is implemented.",
        "expected_files": ["order_service.py"],
        "expected_symbols": ["create_order"],
        "expected_relationships": []
    },
    {
        "task_id": "repo002_task002",
        "repository_id": "repo002",
        "task_type": "symbol_localization",
        "task": "Find where the calculate_total function is implemented.",
        "expected_files": ["pricing.py"],
        "expected_symbols": ["calculate_total"],
        "expected_relationships": []
    },
    {
        "task_id": "repo002_task003",
        "repository_id": "repo002",
        "task_type": "symbol_localization",
        "task": "Find where the apply_discount function is implemented.",
        "expected_files": ["discounts.py"],
        "expected_symbols": ["apply_discount"],
        "expected_relationships": []
    },
    {
        "task_id": "repo002_task004",
        "repository_id": "repo002",
        "task_type": "path_reasoning",
        "task": "Trace the function call from run in main.py to create_order in order_service.py.",
        "expected_files": ["main.py", "order_service.py"],
        "expected_symbols": ["run", "create_order"],
        "expected_relationships": [
            "main.py:run -> order_service.py:create_order"
        ]
    },
    {
        "task_id": "repo002_task005",
        "repository_id": "repo002",
        "task_type": "path_reasoning",
        "task": "Trace how create_order calls calculate_total across the order service and pricing modules.",
        "expected_files": ["order_service.py", "pricing.py"],
        "expected_symbols": ["create_order", "calculate_total"],
        "expected_relationships": [
            "order_service.py:create_order -> pricing.py:calculate_total"
        ]
    },
    {
        "task_id": "repo002_task006",
        "repository_id": "repo002",
        "task_type": "path_reasoning",
        "task": "Trace how calculate_total delegates the discount calculation to apply_discount.",
        "expected_files": ["pricing.py", "discounts.py"],
        "expected_symbols": ["calculate_total", "apply_discount"],
        "expected_relationships": [
            "pricing.py:calculate_total -> discounts.py:apply_discount"
        ]
    },
    {
        "task_id": "repo002_task007",
        "repository_id": "repo002",
        "task_type": "path_reasoning",
        "task": "Trace the order-processing flow from run in main.py through create_order to calculate_total in pricing.py. Return the files, symbols, and direct function-call relationships involved.",
        "expected_files": ["main.py", "order_service.py", "pricing.py"],
        "expected_symbols": ["run", "create_order", "calculate_total"],
        "expected_relationships": [
            "main.py:run -> order_service.py:create_order",
            "order_service.py:create_order -> pricing.py:calculate_total"
        ]
    },
    {
        "task_id": "repo002_task008",
        "repository_id": "repo002",
        "task_type": "path_reasoning",
        "task": "Trace the complete function-call chain from run in main.py to apply_discount in discounts.py. Return all participating files, symbols, and direct function-call relationships.",
        "expected_files": [
            "main.py",
            "order_service.py",
            "pricing.py",
            "discounts.py"
        ],
        "expected_symbols": [
            "run",
            "create_order",
            "calculate_total",
            "apply_discount"
        ],
        "expected_relationships": [
            "main.py:run -> order_service.py:create_order",
            "order_service.py:create_order -> pricing.py:calculate_total",
            "pricing.py:calculate_total -> discounts.py:apply_discount"
        ]
    }
]

existing_ids = {task["task_id"] for task in original_tasks}
new_ids = [task["task_id"] for task in tasks_to_add]

if len(new_ids) != len(set(new_ids)) or existing_ids.intersection(new_ids):
    raise RuntimeError("Duplicate task IDs detected. No changes made.")

# Preserve the original task objects and append new tasks.
benchmark["tasks"].extend(tasks_to_add)
metadata["repositories"].append(new_repository)
benchmark["version"] = "0.3"

# Validate the complete proposed data before writing.
all_ids = [task["task_id"] for task in benchmark["tasks"]]
if len(all_ids) != len(set(all_ids)):
    raise RuntimeError("Task IDs are not unique. No changes made.")

if len(benchmark["tasks"]) != 18:
    raise RuntimeError("Expected exactly 18 tasks. No changes made.")

if len(metadata["repositories"]) != 2:
    raise RuntimeError("Expected exactly 2 registered repositories. No changes made.")

# Write JSON only after validation.
metadata_path.write_text(
    json.dumps(metadata, indent=4, ensure_ascii=False) + "\n",
    encoding="utf-8"
)
tasks_path.write_text(
    json.dumps(benchmark, indent=4, ensure_ascii=False) + "\n",
    encoding="utf-8"
)

print("\nBENCHMARK UPDATE SUCCESSFUL")
print(f"Benchmark version: {benchmark['version']}")
print(f"Repositories: {len(metadata['repositories'])}")
print(f"Original tasks preserved: {original_task_count}")
print(f"New tasks added: {len(tasks_to_add)}")
print(f"Total tasks: {len(benchmark['tasks'])}")
print("New task IDs:", ", ".join(new_ids))
print("\nExisting experiment result files have NOT been changed.")
