# Graph-Augmented Repository Reasoning: A Comparative Evaluation of Structural and Conventional Retrieval

## Abstract

Understanding multi-file software repositories is a challenging task for automated coding agents. Conventional repository retrieval can identify relevant files and symbols, but may fail to recover relationships across modules. This study investigates whether graph-augmented repository reasoning improves repository-level question answering compared with a baseline retrieval approach.

We evaluate two approaches on a benchmark containing 18 tasks across two local Python repositories. Both approaches are evaluated using primary-file accuracy, file-set exact match, symbol exact match, relationship exact match, and complete-answer exact match.

The graph-augmented approach achieves higher scores across all five reported accuracy metrics. In particular, file-set exact match improves from 33.3% to 83.3%, while complete-answer exact match improves from 33.3% to 66.7%.

These results suggest that structural repository information can improve repository-level reasoning on the evaluated benchmark. However, the limited benchmark size and deterministic agent implementations mean that the findings should be interpreted as preliminary evidence rather than a general conclusion about large or small language models.

## 1. Introduction

Software repositories contain interconnected files, functions, classes, imports, and function-call relationships.

When answering repository-level questions, an agent must identify not only the relevant source file but also the symbols and dependencies involved in a particular workflow.

Conventional retrieval approaches may retrieve relevant code through lexical or semantic matching. However, retrieving individual files does not necessarily reveal how different components interact.

Graph-augmented repository reasoning addresses this challenge by representing structural relationships between repository elements and using those relationships to support retrieval.

This research compares conventional repository retrieval with graph-augmented repository reasoning.

## 2. Research Question

Can graph-augmented repository reasoning improve the accuracy and completeness of repository-level answers compared with conventional repository retrieval?

## 3. Hypothesis

Graph-augmented retrieval may improve repository-level reasoning by providing additional structural context, particularly for tasks requiring identification of multiple files, symbols, and function-call relationships.

This hypothesis is evaluated experimentally rather than assumed to be true.

## 4. Methodology

### 4.1 Experimental Setup

The experiment uses two local Python repositories:

- Sample repository (`repo001`)
- Order application repository (`repo002`)

The benchmark contains 18 repository-level tasks distributed across these repositories.

Each task is evaluated using two approaches:

1. Baseline repository retrieval.
2. Graph-augmented repository reasoning.

This produces 36 total agent runs: 18 for each approach.

### 4.2 Baseline Approach

The baseline agent uses conventional repository retrieval to identify relevant repository information and construct structured answers.

It serves as the comparison approach for evaluating the contribution of graph-based structural reasoning.

### 4.3 Graph-Augmented Approach

The graph-augmented agent uses repository structure and relationships to support the identification of relevant files, symbols, and function-call dependencies.

The approach is designed to improve answers to questions involving multi-file workflows and relationships between software components.

### 4.4 Evaluation Metrics

The experiment uses the following metrics:

- **Primary-file accuracy:** Whether the predicted primary file matches the expected primary file.
- **File-set exact match:** Whether the complete predicted file set matches the expected file set.
- **Symbol exact match:** Whether the predicted symbols match the expected symbols.
- **Relationship exact match:** Whether the predicted relationships match the expected relationships.
- **Complete-answer exact match:** Whether the complete structured answer matches the expected answer.

Additional precision, recall, and F1 metrics are recorded for files, symbols, and relationships.

## 5. Experimental Results

The v0.6 experiment completed successfully with 36 total runs and no recorded execution failures.

### 5.1 Comparative Results

| Evaluation Metric | Baseline | Graph-Augmented |
|---|---:|---:|
| Primary-file accuracy | 77.78% | 83.33% |
| File-set exact match | 33.33% | 83.33% |
| Symbol exact match | 33.33% | 72.22% |
| Relationship exact match | 50.00% | 83.33% |
| Complete-answer exact match | 33.33% | 66.67% |

### 5.2 Results Analysis

The graph-augmented approach outperformed the baseline on all five reported accuracy metrics.

The largest improvement was observed in file-set exact match, increasing from 33.33% to 83.33%, a difference of 50 percentage points.

Symbol exact match increased by approximately 38.89 percentage points, while relationship exact match increased by approximately 33.33 percentage points.

Complete-answer exact match increased from 33.33% to 66.67%.

These findings indicate that repository structural information may be particularly useful for tasks requiring multiple files and relationships between functions.

However, the results are limited to the repositories and tasks included in this experiment.

## 6. Discussion

The results provide preliminary evidence that graph-augmented repository reasoning can improve structured repository question answering.

The improvement in file-set and relationship exact match is especially relevant because multi-file software workflows frequently depend on interactions between different modules.

The graph-augmented approach also achieved higher complete-answer accuracy, suggesting that structural context can contribute to more complete answers.

Nevertheless, higher benchmark accuracy does not establish that graph augmentation will improve every coding-agent task or every repository.

The experiment evaluates repository reasoning and structured answer retrieval. It does not measure code modification quality, software test success, or autonomous software engineering performance.

## 7. Limitations

This study has several limitations:

1. The benchmark contains only 18 tasks.
2. Only two local Python repositories were evaluated.
3. The experiment does not establish generalization to large production repositories.
4. The active agent implementations use deterministic retrieval and heuristic reasoning; this experiment does not establish Gemma 4 model performance.
5. The experiment evaluates structured repository answers rather than end-to-end code generation or code repair.
6. The relationship precision and F1 results require careful interpretation alongside exact-match scores.
7. The number of tasks is too small to support strong statistical generalization claims.

Future experiments should use more repositories, larger benchmarks, repeated evaluations, and controlled comparisons with language-model-based agents.

## 8. Conclusion

This study compared conventional repository retrieval with graph-augmented repository reasoning across 18 tasks in two Python repositories.

The graph-augmented approach achieved higher accuracy across all five reported evaluation metrics. The most substantial improvement occurred in file-set exact match, which increased from 33.33% to 83.33%.

The findings suggest that incorporating repository structure and function-call relationships can improve structured repository reasoning on the evaluated benchmark.

Further evaluation on larger and more diverse repositories is required to establish the general applicability of this approach.

## 9. Future Work

Potential future directions include:

- Evaluating the approach on larger open-source repositories.
- Integrating Gemma-family language models into the repository reasoning pipeline.
- Comparing graph-augmented retrieval with language-model-based semantic retrieval.
- Evaluating code modification and test execution success.
- Measuring retrieval latency, context size, and computational cost.
- Performing ablation studies to identify the contribution of individual graph components.

## 10. Experimental Artifacts

The v0.6 experiment generated the following artifacts:

- `results/logs/multi_repository_results_v0_6.json`
- `results/metrics/multi_repository_comparison_v0_6.csv`
- `results/metrics/multi_repository_summary_v0_6.csv`

These files contain the detailed experimental records, task-level comparisons, and aggregate evaluation metrics.