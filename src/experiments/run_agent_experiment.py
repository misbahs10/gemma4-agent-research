
import csv
import json
import sys
from pathlib import Path
from statistics import mean


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent.baseline_agent import BaselineCodingAgent
from agent.graph_agent import GraphAugmentedCodingAgent


TASKS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "agent_tasks.json"
)

REPOSITORY_PATH = (
    PROJECT_ROOT / "data" / "raw" / "sample_repo"
)

RESULTS_DIR = PROJECT_ROOT / "results"
LOGS_DIR = RESULTS_DIR / "logs"
METRICS_DIR = RESULTS_DIR / "metrics"


# Versioned outputs preserve all existing experiment results.
JSON_OUTPUT = LOGS_DIR / "agent_experiment_results_10tasks_v2.json"
COMPARISON_OUTPUT = METRICS_DIR / "agent_comparison_10tasks_v2.csv"
SUMMARY_OUTPUT = METRICS_DIR / "agent_summary_10tasks_v2.csv"


# ==================================================
# DATA HELPERS
# ==================================================

def as_list(value):
    """Normalize optional values into lists."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def normalize_items(items):
    """Normalize strings and structured relationships."""
    normalized = set()

    for item in as_list(items):
        if item is None:
            continue

        if isinstance(item, dict):
            source = item.get("source")
            target = item.get("target")
            relation_type = item.get("type")

            if source is not None and target is not None:
                value = f"{source} -> {target}"
                if relation_type:
                    value += f" [{relation_type}]"
            else:
                value = json.dumps(
                    item, sort_keys=True, ensure_ascii=False
                )
        else:
            value = str(item)

        value = " ".join(value.strip().lower().split())

        if value:
            normalized.add(value)

    return normalized


def calculate_precision(predicted, expected):
    predicted_set = normalize_items(predicted)
    expected_set = normalize_items(expected)

    if not predicted_set:
        return 0.0

    return len(predicted_set & expected_set) / len(predicted_set)


def calculate_recall(predicted, expected):
    predicted_set = normalize_items(predicted)
    expected_set = normalize_items(expected)

    if not expected_set:
        return None

    return len(predicted_set & expected_set) / len(expected_set)


def calculate_exact_match(predicted, expected):
    return normalize_items(predicted) == normalize_items(expected)


def safe_mean(values):
    """Average available numeric values only."""
    valid = [
        value
        for value in values
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
    ]

    return round(mean(valid), 4) if valid else None


# ==================================================
# LOAD TASKS
# ==================================================

def load_tasks():
    if not TASKS_PATH.exists():
        raise FileNotFoundError(
            f"Task file not found: {TASKS_PATH}"
        )

    with TASKS_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Support either {"tasks": [...]} or a plain list.
    tasks = data.get("tasks", []) if isinstance(data, dict) else data

    if not isinstance(tasks, list) or not tasks:
        raise ValueError(
            "The task file must contain a non-empty task list."
        )

    required_fields = {"id", "task"}

    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError(f"Task #{index} must be a dictionary.")

        missing = required_fields - task.keys()
        if missing:
            raise ValueError(
                f"Task #{index} is missing fields: {sorted(missing)}"
            )

    print(f"Loaded tasks: {len(tasks)}")
    return tasks


# ==================================================
# EXTRACT AGENT ANSWER
# ==================================================

def extract_predictions(result):
    """Extract structured predictions from an agent result."""
    answer = result.get("answer", {})

    if not isinstance(answer, dict):
        answer = {}

    predicted_files = answer.get("files")

    if predicted_files is None:
        predicted_files = result.get("answer_files")

    if predicted_files is None:
        predicted_files = result.get("retrieved_files")

    if not predicted_files and result.get("primary_file"):
        predicted_files = [result["primary_file"]]

    return {
        "predicted_files": as_list(predicted_files),
        "predicted_symbols": as_list(answer.get("symbols", [])),
        "predicted_relationships": as_list(
            answer.get("relationships", [])
        ),
    }


def get_optional_count(result, key):
    """
    Return a count only if the agent actually supplies the field.
    Missing instrumentation must not be reported as zero.
    """
    if key not in result:
        return None

    value = result[key]

    if isinstance(value, list):
        return len(value)

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value

    return None


# ==================================================
# EVALUATE ONE RESULT
# ==================================================

def evaluate_result(task_item, agent_name, result):
    expected_files = as_list(task_item.get("expected_files"))
    expected_symbols = as_list(task_item.get("expected_symbols"))
    expected_relationships = as_list(
        task_item.get("expected_relationships")
    )

    predictions = extract_predictions(result)

    predicted_files = predictions["predicted_files"]
    predicted_symbols = predictions["predicted_symbols"]
    predicted_relationships = predictions["predicted_relationships"]

    file_precision = calculate_precision(
        predicted_files, expected_files
    )
    file_recall = calculate_recall(
        predicted_files, expected_files
    )
    file_exact_match = calculate_exact_match(
        predicted_files, expected_files
    )

    if expected_symbols:
        symbol_precision = calculate_precision(
            predicted_symbols, expected_symbols
        )
        symbol_recall = calculate_recall(
            predicted_symbols, expected_symbols
        )
        symbol_exact_match = calculate_exact_match(
            predicted_symbols, expected_symbols
        )
    else:
        symbol_precision = None
        symbol_recall = None
        symbol_exact_match = None

    if expected_relationships:
        relationship_precision = calculate_precision(
            predicted_relationships, expected_relationships
        )
        relationship_recall = calculate_recall(
            predicted_relationships, expected_relationships
        )
        relationship_exact_match = calculate_exact_match(
            predicted_relationships, expected_relationships
        )
    else:
        relationship_precision = None
        relationship_recall = None
        relationship_exact_match = None

    return {
        "task_id": task_item["id"],
        "task": task_item["task"],
        "task_type": task_item.get("task_type", ""),
        "agent": agent_name,
        "status": result.get("status", "unknown"),

        "expected_files": expected_files,
        "predicted_files": predicted_files,
        "expected_symbols": expected_symbols,
        "predicted_symbols": predicted_symbols,
        "expected_relationships": expected_relationships,
        "predicted_relationships": predicted_relationships,

        "file_exact_match": file_exact_match,
        "file_precision": round(file_precision, 4),
        "file_recall": (
            round(file_recall, 4)
            if file_recall is not None else None
        ),

        "symbol_exact_match": symbol_exact_match,
        "symbol_precision": (
            round(symbol_precision, 4)
            if symbol_precision is not None else None
        ),
        "symbol_recall": (
            round(symbol_recall, 4)
            if symbol_recall is not None else None
        ),

        "relationship_exact_match": relationship_exact_match,
        "relationship_precision": (
            round(relationship_precision, 4)
            if relationship_precision is not None else None
        ),
        "relationship_recall": (
            round(relationship_recall, 4)
            if relationship_recall is not None else None
        ),

        # None means instrumentation is unavailable, not zero calls.
        "tool_calls": get_optional_count(result, "tool_calls"),
        "graph_dependency_count": get_optional_count(
            result, "graph_dependencies"
        ),
    }


# ==================================================
# BUILD SUMMARY
# ==================================================

def build_summary(all_results, agent_names):
    summary = []

    for agent_name in agent_names:
        agent_results = [
            row for row in all_results
            if row["agent"] == agent_name
        ]

        successful = [
            row for row in agent_results
            if row["status"] != "error"
        ]

        def average_metric(key):
            return safe_mean([
                row[key] for row in successful
                if row.get(key) is not None
            ])

        summary.append({
            "agent": agent_name,
            "total_tasks": len(agent_results),
            "successful_tasks": len(successful),
            "failed_tasks": len(agent_results) - len(successful),

            "file_exact_match_rate": safe_mean([
                float(row["file_exact_match"])
                for row in successful
            ]),
            "average_file_precision": average_metric("file_precision"),
            "average_file_recall": average_metric("file_recall"),

            "symbol_exact_match_rate": safe_mean([
                float(row["symbol_exact_match"])
                for row in successful
                if row["symbol_exact_match"] is not None
            ]),
            "average_symbol_precision": average_metric(
                "symbol_precision"
            ),
            "average_symbol_recall": average_metric("symbol_recall"),

            "relationship_exact_match_rate": safe_mean([
                float(row["relationship_exact_match"])
                for row in successful
                if row["relationship_exact_match"] is not None
            ]),
            "average_relationship_precision": average_metric(
                "relationship_precision"
            ),
            "average_relationship_recall": average_metric(
                "relationship_recall"
            ),

            "average_tool_calls": average_metric("tool_calls"),
        })

    return summary


# ==================================================
# SAVE OUTPUTS
# ==================================================

def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_csv(path, rows):
    if not rows:
        raise ValueError(f"Cannot save an empty CSV: {path}")

    fields = list(dict.fromkeys(
        key for row in rows for key in row.keys()
    ))

    with path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=fields, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


# ==================================================
# RUN EXPERIMENT
# ==================================================

def run_experiment():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks()

    if not REPOSITORY_PATH.is_dir():
        raise FileNotFoundError(
            f"Sample repository not found: {REPOSITORY_PATH}"
        )

    agents = [
        (
            "baseline",
            BaselineCodingAgent(
                repository_path=str(REPOSITORY_PATH)
            ),
        ),
        (
            "graph_augmented",
            GraphAugmentedCodingAgent(
                repository_path=str(REPOSITORY_PATH)
            ),
        ),
    ]

    all_results = []
    total_runs = len(tasks) * len(agents)
    current_run = 0

    for task_item in tasks:
        task_id = task_item["id"]
        task_text = task_item["task"]
        task_type = task_item.get("task_type")

        print(f"\nTask {task_id}: {task_text}")
        print(f"Task type: {task_type or 'unspecified'}")

        for agent_name, agent in agents:
            current_run += 1
            print(f"[{current_run}/{total_runs}] Running {agent_name}...")

            try:
                # IMPORTANT: Pass the task type to both agents.
                result = agent.run(
                    task_text,
                    task_type=task_type,
                )

                if not isinstance(result, dict):
                    raise TypeError(
                        "Agent.run() must return a dictionary."
                    )

                record = evaluate_result(
                    task_item=task_item,
                    agent_name=agent_name,
                    result=result,
                )

            except Exception as error:
                record = {
                    "task_id": task_id,
                    "task": task_text,
                    "task_type": task_type or "",
                    "agent": agent_name,
                    "status": "error",
                    "error": str(error),

                    "expected_files": as_list(
                        task_item.get("expected_files")
                    ),
                    "predicted_files": [],
                    "expected_symbols": as_list(
                        task_item.get("expected_symbols")
                    ),
                    "predicted_symbols": [],
                    "expected_relationships": as_list(
                        task_item.get("expected_relationships")
                    ),
                    "predicted_relationships": [],

                    "file_exact_match": False,
                    "file_precision": 0.0,
                    "file_recall": 0.0,

                    "symbol_exact_match": None,
                    "symbol_precision": None,
                    "symbol_recall": None,

                    "relationship_exact_match": None,
                    "relationship_precision": None,
                    "relationship_recall": None,

                    "tool_calls": None,
                    "graph_dependency_count": None,
                }

                print(f"  ERROR: {error}")

            all_results.append(record)

            print(
                f"  Status: {record['status']} | "
                f"File exact match: {record['file_exact_match']} | "
                f"Symbol exact match: {record['symbol_exact_match']} | "
                f"Relationship exact match: "
                f"{record['relationship_exact_match']}"
            )

    # Save versioned results; existing experiment files remain untouched.
    save_json(JSON_OUTPUT, all_results)
    save_csv(COMPARISON_OUTPUT, all_results)

    summary = build_summary(
        all_results,
        [name for name, _ in agents],
    )
    save_csv(SUMMARY_OUTPUT, summary)

    print("\n" + "=" * 65)
    print("10-TASK EXPERIMENT V2 COMPLETED")
    print("=" * 65)

    for item in summary:
        print(f"\nAgent: {item['agent']}")
        print(f"Tasks: {item['total_tasks']}")
        print(f"Successful: {item['successful_tasks']}")
        print(f"Failed: {item['failed_tasks']}")
        print(f"File exact-match rate: {item['file_exact_match_rate']}")
        print(f"Symbol exact-match rate: {item['symbol_exact_match_rate']}")
        print(
            "Relationship exact-match rate: "
            f"{item['relationship_exact_match_rate']}"
        )
        print(f"Average tool calls: {item['average_tool_calls']}")

    print("\nSaved files:")
    print(JSON_OUTPUT)
    print(COMPARISON_OUTPUT)
    print(SUMMARY_OUTPUT)


if __name__ == "__main__":
    run_experiment()

