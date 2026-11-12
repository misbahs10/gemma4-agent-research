
import csv
import json
from pathlib import Path

from agent.baseline_agent import BaselineCodingAgent
from agent.graph_agent import GraphAugmentedCodingAgent

from evaluation.benchmark_loader import BenchmarkLoader
from evaluation.repository_resolver import RepositoryResolver


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = PROJECT_ROOT / "benchmark"
RESULTS_ROOT = PROJECT_ROOT / "results"

METRICS_DIR = RESULTS_ROOT / "metrics"
LOGS_DIR = RESULTS_ROOT / "logs"


# ==========================================================
# NORMALIZATION HELPERS
# ==========================================================

def normalize_files(files):
    """Normalize file paths to unique, lowercase file names."""
    normalized = set()

    for item in files or []:
        if not item:
            continue

        name = (
            str(item)
            .replace("\\", "/")
            .split("/")[-1]
            .strip()
            .lower()
        )

        if name:
            normalized.add(name)

    return normalized


def normalize_items(items):
    """Normalize symbols or relationships for comparison."""
    return {
        " ".join(str(item).strip().lower().split())
        for item in (items or [])
        if item is not None and str(item).strip()
    }


def calculate_precision(predicted, expected):
    predicted_set = set(predicted)
    expected_set = set(expected)

    if not predicted_set:
        return 0.0

    return len(predicted_set & expected_set) / len(predicted_set)


def calculate_recall(predicted, expected):
    predicted_set = set(predicted)
    expected_set = set(expected)

    if not expected_set:
        return 1.0 if not predicted_set else 0.0

    return len(predicted_set & expected_set) / len(expected_set)


def calculate_f1(precision, recall):
    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


# ==========================================================
# RESULT EXTRACTION
# ==========================================================


def extract_answer(result):
    """Extract a standardized answer from either flat or nested results."""

    answer = result.get("answer", result)

    if not isinstance(answer, dict):
        answer = result

    predicted_files = answer.get("files", [])

    if not predicted_files:
        predicted_files = result.get("answer_files", [])

    if not predicted_files:
        primary = (
            result.get("selected_file")
            or result.get("primary_file")
        )
        if primary:
            predicted_files = [primary]

    predicted_symbols = answer.get("symbols", [])
    predicted_relationships = answer.get("relationships", [])

    primary_file = (
        result.get("selected_file")
        or result.get("primary_file")
        or (predicted_files[0] if predicted_files else "")
    )

    return {
        "primary_file": primary_file or "",
        "files": list(predicted_files or []),
        "symbols": list(predicted_symbols or []),
        "relationships": list(predicted_relationships or []),
    }


def count_tool_calls(result):
    """Count recorded tool observations."""
    return len(result.get("observations", []))

# ==========================================================
# EVALUATION
# ==========================================================

def evaluate_result(result, task_item):
    """Evaluate an agent result against benchmark ground truth."""

    answer = extract_answer(result)

    expected_files = task_item.get("expected_files", [])
    expected_symbols = task_item.get("expected_symbols", [])
    expected_relationships = task_item.get(
        "expected_relationships", []
    )

    predicted_files = normalize_files(answer["files"])
    expected_file_set = normalize_files(expected_files)

    predicted_symbols = normalize_items(answer["symbols"])
    expected_symbol_set = normalize_items(expected_symbols)

    predicted_relationships = normalize_items(
        answer["relationships"]
    )
    expected_relationship_set = normalize_items(
        expected_relationships
    )

    primary_file = normalize_files([answer["primary_file"]])
    primary_file_match = bool(
        primary_file & expected_file_set
    )

    file_set_match = predicted_files == expected_file_set
    symbol_set_match = predicted_symbols == expected_symbol_set
    relationship_set_match = (
        predicted_relationships == expected_relationship_set
    )

    complete_answer_match = (
        file_set_match
        and symbol_set_match
        and relationship_set_match
    )

    file_precision = calculate_precision(
        predicted_files, expected_file_set
    )
    file_recall = calculate_recall(
        predicted_files, expected_file_set
    )

    symbol_precision = calculate_precision(
        predicted_symbols, expected_symbol_set
    )
    symbol_recall = calculate_recall(
        predicted_symbols, expected_symbol_set
    )

    relationship_precision = calculate_precision(
        predicted_relationships, expected_relationship_set
    )
    relationship_recall = calculate_recall(
        predicted_relationships, expected_relationship_set
    )

    return {
        "primary_file": answer["primary_file"],
        "predicted_files": answer["files"],
        "predicted_symbols": answer["symbols"],
        "predicted_relationships": answer["relationships"],

        "primary_file_match": primary_file_match,
        "file_set_exact_match": file_set_match,
        "symbol_exact_match": symbol_set_match,
        "relationship_exact_match": relationship_set_match,
        "complete_answer_exact_match": complete_answer_match,

        "file_precision": file_precision,
        "file_recall": file_recall,

        "symbol_precision": symbol_precision,
        "symbol_recall": symbol_recall,

        "relationship_precision": relationship_precision,
        "relationship_recall": relationship_recall,
        "relationship_f1": calculate_f1(
            relationship_precision,
            relationship_recall,
        ),

        "tool_calls": count_tool_calls(result),
        "graph_dependency_count": len(
            result.get("graph_dependencies", [])
        ),
    }


# ==========================================================
# RUN EXPERIMENT
# ==========================================================

def run_experiment(loader, resolver):
    """Run both agents on every benchmark task."""

    tasks = loader.load_tasks()
    results = []

    repository_ids = sorted({
        task["repository_id"] for task in tasks
    })

    for repository_id in repository_ids:
        repository_path = resolver.resolve(repository_id)

        repository_tasks = [
            task for task in tasks
            if task["repository_id"] == repository_id
        ]

        agents = [
            (
                "baseline",
                BaselineCodingAgent(str(repository_path)),
            ),
            (
                "graph_augmented",
                GraphAugmentedCodingAgent(str(repository_path)),
            ),
        ]

        print("\n" + "=" * 75)
        print(f"Repository: {repository_id}")
        print(f"Path: {repository_path}")
        print("=" * 75)

        for task_item in repository_tasks:
            task_id = task_item["task_id"]
            task_text = task_item["task"]
            task_type = task_item.get("task_type")

            print(f"\nTask: {task_id}")
            print(task_text)

            for agent_name, agent in agents:
                print(f"\nRunning: {agent_name}")

                try:
                    result = agent.run(
                        task_text,
                        task_type=task_type,
                    )

                    metrics = evaluate_result(result, task_item)

                    record = {
                        "repository_id": repository_id,
                        "task_id": task_id,
                        "task_type": task_type or "",
                        "task": task_text,
                        "agent": agent_name,
                        "status": result.get("status", "completed"),
                        "expected_files": task_item.get(
                            "expected_files", []
                        ),
                        "expected_symbols": task_item.get(
                            "expected_symbols", []
                        ),
                        "expected_relationships": task_item.get(
                            "expected_relationships", []
                        ),
                        **metrics,
                    }

                except Exception as exc:
                    # Preserve failed runs in the results.
                    record = {
                        "repository_id": repository_id,
                        "task_id": task_id,
                        "task_type": task_type or "",
                        "task": task_text,
                        "agent": agent_name,
                        "status": "error",
                        "error": f"{type(exc).__name__}: {exc}",
                        "expected_files": task_item.get(
                            "expected_files", []
                        ),
                        "expected_symbols": task_item.get(
                            "expected_symbols", []
                        ),
                        "expected_relationships": task_item.get(
                            "expected_relationships", []
                        ),
                        "primary_file": "",
                        "predicted_files": [],
                        "predicted_symbols": [],
                        "predicted_relationships": [],
                        "primary_file_match": False,
                        "file_set_exact_match": False,
                        "symbol_exact_match": False,
                        "relationship_exact_match": False,
                        "complete_answer_exact_match": False,
                        "file_precision": 0.0,
                        "file_recall": 0.0,
                        "symbol_precision": 0.0,
                        "symbol_recall": 0.0,
                        "relationship_precision": 0.0,
                        "relationship_recall": 0.0,
                        "relationship_f1": 0.0,
                        "tool_calls": 0,
                        "graph_dependency_count": 0,
                    }

                results.append(record)

                print(f"Status: {record['status']}")
                print(
                    "Primary file match:",
                    record["primary_file_match"],
                )
                print(
                    "File-set exact match:",
                    record["file_set_exact_match"],
                )
                print(
                    "Symbol exact match:",
                    record["symbol_exact_match"],
                )
                print(
                    "Relationship exact match:",
                    record["relationship_exact_match"],
                )
                print(
                    "Complete-answer exact match:",
                    record["complete_answer_exact_match"],
                )

                if record.get("error"):
                    print("Error:", record["error"])

    return results


# ==========================================================
# SUMMARY
# ==========================================================

def mean(values):
    return sum(values) / len(values) if values else 0.0


def save_summary(results, output_file):
    """Save aggregate metrics for each agent."""

    agent_names = sorted({
        record["agent"] for record in results
    })

    summary = []

    metric_fields = [
        "primary_file_match",
        "file_set_exact_match",
        "symbol_exact_match",
        "relationship_exact_match",
        "complete_answer_exact_match",
        "file_precision",
        "file_recall",
        "symbol_precision",
        "symbol_recall",
        "relationship_precision",
        "relationship_recall",
        "relationship_f1",
        "tool_calls",
    ]

    for agent_name in agent_names:
        agent_records = [
            record for record in results
            if record["agent"] == agent_name
        ]

        total = len(agent_records)
        successful = sum(
            record["status"] == "completed"
            for record in agent_records
        )

        row = {
            "agent": agent_name,
            "total_tasks": total,
            "successful_runs": successful,
            "failed_runs": total - successful,
        }

        for field in metric_fields:
            row[field] = mean([
                float(record.get(field, 0))
                for record in agent_records
            ])

        # Explicitly named rate columns for clarity.
        row["exact_match_rate"] = row["primary_file_match"]
        row["file_set_exact_match_rate"] = (
            row["file_set_exact_match"]
        )
        row["symbol_exact_match_rate"] = (
            row["symbol_exact_match"]
        )
        row["relationship_exact_match_rate"] = (
            row["relationship_exact_match"]
        )
        row["complete_answer_exact_match_rate"] = (
            row["complete_answer_exact_match"]
        )

        summary.append(row)

    if not summary:
        print("No results available; summary was not written.")
        return

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(summary[0].keys()),
        )
        writer.writeheader()
        writer.writerows(summary)


# ==========================================================
# SAVE RESULTS
# ==========================================================

def json_safe(record):
    """Convert values into JSON-serializable Python objects."""
    return record


def save_json(results, output_file):
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            [json_safe(record) for record in results],
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_csv(results, output_file):
    if not results:
        print("No results available; detailed CSV was not written.")
        return

    fieldnames = list(dict.fromkeys(
        key
        for record in results
        for key in record.keys()
    ))

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()

        for record in results:
            row = record.copy()

            for key, value in row.items():
                if isinstance(value, (list, dict, set)):
                    row[key] = json.dumps(
                        value,
                        ensure_ascii=False,
                    )

            writer.writerow(row)


# ==========================================================
# MAIN
# ==========================================================

def main():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    loader = BenchmarkLoader(str(BENCHMARK_ROOT))

    repositories = loader.load_repositories()

    resolver = RepositoryResolver(
        str(PROJECT_ROOT),
        repositories,
    )

    print("=" * 75)
    print("REPOSITORY GRAPH REASONING EXPERIMENT")
    print("=" * 75)
    print(f"Benchmark: {BENCHMARK_ROOT}")
    print(f"Repositories: {len(repositories)}")

    results = run_experiment(loader, resolver)

    detailed_json = LOGS_DIR / "multi_repository_results_v0_6.json"
    detailed_csv = METRICS_DIR / "multi_repository_comparison_v0_6.csv"
    summary_csv = METRICS_DIR / "multi_repository_summary_v0_6.csv"

    save_json(results, detailed_json)
    save_csv(results, detailed_csv)
    save_summary(results, summary_csv)

    print("\n" + "=" * 75)
    print("EXPERIMENT COMPLETED")
    print("=" * 75)
    print(f"Total agent runs: {len(results)}")
    print(f"Detailed JSON: {detailed_json}")
    print(f"Detailed CSV: {detailed_csv}")
    print(f"Summary CSV: {summary_csv}")

    print("\nSummary:")
    for agent_name in sorted({
        record["agent"] for record in results
    }):
        agent_records = [
            record for record in results
            if record["agent"] == agent_name
        ]

        print(f"\n{agent_name}")
        print(
            "  Primary-file accuracy:",
            f"{mean([float(r['primary_file_match']) for r in agent_records]):.3f}",
        )
        print(
            "  File-set exact match:",
            f"{mean([float(r['file_set_exact_match']) for r in agent_records]):.3f}",
        )
        print(
            "  Symbol exact match:",
            f"{mean([float(r['symbol_exact_match']) for r in agent_records]):.3f}",
        )
        print(
            "  Relationship exact match:",
            f"{mean([float(r['relationship_exact_match']) for r in agent_records]):.3f}",
        )
        print(
            "  Complete-answer exact match:",
            f"{mean([float(r['complete_answer_exact_match']) for r in agent_records]):.3f}",
        )


if __name__ == "__main__":
    main()
