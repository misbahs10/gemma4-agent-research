# Graph-Augmented Repository Reasoning

A comparative research project investigating whether graph-augmented repository reasoning can improve structured software repository question answering compared with conventional repository retrieval.

## Research Overview

Software repositories contain interconnected files, functions, classes, imports, and function-call relationships. Finding the correct source file is not always sufficient to understand how a feature or workflow operates across multiple modules.

This project compares two repository reasoning approaches:

1. **Baseline:** Conventional repository retrieval.
2. **Graph-Augmented:** Repository retrieval supported by structural information and code relationships.

The goal is to evaluate whether structural context improves the accuracy and completeness of repository-level answers.

> **Scope clarification:** The current v0.6 experiment evaluates deterministic retrieval and graph-reasoning implementations. It does not measure Gemma 4 model performance or end-to-end autonomous code generation.

## Research Question

Can graph-augmented repository reasoning improve repository-level answer accuracy compared with conventional repository retrieval?

## Benchmark

The benchmark contains:

- 2 local Python repositories.
- 18 repository-level tasks.
- 36 total agent runs.
- 18 runs per approach.

The tasks evaluate source-file identification, symbol identification, and function-call relationships, including multi-file workflows.

## Experimental Results

Results from experiment **v0.6**:

| Metric | Baseline | Graph-Augmented |
|---|---:|---:|
| Primary-file accuracy | 77.78% | 83.33% |
| File-set exact match | 33.33% | 83.33% |
| Symbol exact match | 33.33% | 72.22% |
| Relationship exact match | 50.00% | 83.33% |
| Complete-answer exact match | 33.33% | 66.67% |

The graph-augmented approach achieved higher scores across all five reported metrics. The largest difference was in file-set exact match, which improved by 50 percentage points.

These are preliminary results from a small benchmark and should not be treated as proof of general performance across all software repositories.

## Evaluation Metrics

- **Primary-file accuracy:** Correct identification of the primary source file.
- **File-set exact match:** Exact match between predicted and expected file sets.
- **Symbol exact match:** Exact match between predicted and expected symbols.
- **Relationship exact match:** Exact match between predicted and expected relationships.
- **Complete-answer exact match:** Exact match of the complete structured answer.

The experiment also records file, symbol, and relationship precision, recall, and F1 metrics.

## Project Structure

```text
gemma4-agent-research/
│
├── benchmark/
│   ├── metadata/
│   └── tasks/
│
├── data/
│   └── raw/
│       ├── sample_repo/
│       └── order_app_repo/
│
├── experiments/
│
├── notebooks/
│
├── paper/
│   └── research_notes.md
│
├── results/
│   ├── logs/
│   │   └── multi_repository_results_v0_6.json
│   └── metrics/
│       ├── multi_repository_comparison_v0_6.csv
│       └── multi_repository_summary_v0_6.csv
│
├── src/
│   ├── agent/
│   ├── repository/
│   └── experiments/
│
├── .gitignore
├── README.md
└── requirements.txt
```

*The structure above summarizes the main project components; individual source files may vary.*

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/misbahs10/gemma4-agent-research.git
cd gemma4-agent-research
```

Replace the placeholder URL with the actual repository URL after creating it.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Experiment

Run these commands from the project root directory:

```powershell
$env:PYTHONPATH = "$PWD\src"
python .\src\experiments\run_multi_repository_experiment.py
```

The `PYTHONPATH` setting allows Python to locate the project's source packages.

## Output Files

The v0.6 experiment generates:

| File | Description |
|---|---|
| `results/logs/multi_repository_results_v0_6.json` | Detailed task-level experiment records |
| `results/metrics/multi_repository_comparison_v0_6.csv` | Baseline and graph-augmented comparison |
| `results/metrics/multi_repository_summary_v0_6.csv` | Aggregate evaluation metrics |

## Limitations

- The benchmark contains only 18 tasks.
- Evaluation uses two local Python repositories.
- The current experiment does not evaluate Gemma 4 inference.
- The experiment focuses on structured repository reasoning, not code generation or code repair.
- Larger and more diverse repositories are required to assess generalization.
- Further testing is needed to evaluate performance, scalability, and computational cost.

## Future Work

- Evaluate on larger open-source repositories.
- Integrate and evaluate Gemma-family language models.
- Compare graph retrieval with language-model-based semantic retrieval.
- Evaluate code generation, code repair, and test execution.
- Measure retrieval latency and computational overhead.
- Conduct ablation studies on graph components.

## Research Artifacts

The experimental results are stored in the `results/` directory. The research methodology and findings are documented in `paper/research_notes.md`.

## Conclusion

The v0.6 experiment provides preliminary evidence that graph-augmented repository reasoning can improve structured repository question answering on the evaluated benchmark. Further experiments are required before drawing broader conclusions.
