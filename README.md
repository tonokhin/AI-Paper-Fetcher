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

## Configured Topics

Define repeatable research tracks in `config.yaml`, then fetch one topic:

```bash
PYTHONPATH=src python -m ai_paper_fetcher fetch --config-topic llm_evaluation --max-results 10
```

Fetch every configured topic:

```bash
PYTHONPATH=src python -m ai_paper_fetcher fetch --all --max-results 10
```

Use `--no-download` to save metadata without downloading PDFs:

```bash
PYTHONPATH=src python -m ai_paper_fetcher fetch --all --max-results 10 --no-download
```

Citation counts are enriched from OpenAlex by default when a match is found. To skip that network step:

```bash
PYTHONPATH=src python -m ai_paper_fetcher fetch --all --max-results 10 --no-citations
```

To add or refresh citation counts for an existing reading list:

```bash
PYTHONPATH=src python -m ai_paper_fetcher citations
PYTHONPATH=src python -m ai_paper_fetcher citations --refresh-citations
```

## Features

- Search arXiv by topic or keyword
- Search configured topics from `config.yaml`
- Restrict configured topics by arXiv categories
- Filter by include and exclude keywords
- Add citation counts from OpenAlex when available
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
