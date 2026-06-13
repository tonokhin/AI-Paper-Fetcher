# AI Paper Fetcher

AI Paper Fetcher is a command-line tool that searches arXiv for AI research papers, downloads PDFs, stores metadata, and avoids duplicates across runs.

## Quick Start

```bash
python -m ai_paper_fetcher fetch --topic "LLM evaluation" --max-results 10
```

If you are running from the repository root before installing the package, use:

```bash
PYTHONPATH=src python -m ai_paper_fetcher fetch --topic "LLM evaluation" --max-results 10
```

## Version 1 Features

- Search arXiv by topic or keyword
- Download PDFs into topic-specific folders
- Save metadata to `data/reading_list.csv`
- Track seen papers in `data/seen_papers.json`
- Skip duplicate papers on later runs

## Example Output

```text
Found 10 papers
Downloaded 8 new PDFs
Skipped 2 duplicates
Saved metadata to data/reading_list.csv
```

## Project Plan

See [PROJECT_EXECUTION_PLAN.md](PROJECT_EXECUTION_PLAN.md) for milestones and the full roadmap.
