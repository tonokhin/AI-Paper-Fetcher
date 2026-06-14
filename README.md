# AI Paper Fetcher

AI Paper Fetcher is a command-line tool that searches arXiv for AI research papers, downloads PDFs, stores metadata, and avoids duplicates across runs.

## Quick Start

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
ai-paper-fetcher weekly --max-results 10
```

Fetch one ad hoc topic:

```bash
ai-paper-fetcher fetch --topic "LLM evaluation" --max-results 10
```

## Configured Topics

Define repeatable research tracks in `config.yaml`, then fetch one topic:

```bash
ai-paper-fetcher fetch --config-topic llm_evaluation --max-results 10
```

Fetch every configured topic:

```bash
ai-paper-fetcher fetch --all --max-results 10
```

If many top arXiv results are duplicates you have already seen, keep paging until the tool saves the requested number of new papers:

```bash
ai-paper-fetcher fetch --config-topic llm_evaluation --max-results 10 --new-results --max-pages 5
```

Use `--no-download` to save metadata without downloading PDFs:

```bash
ai-paper-fetcher fetch --all --max-results 10 --no-download
```

Citation counts are enriched from OpenAlex by default when a match is found. To skip that network step:

```bash
ai-paper-fetcher fetch --all --max-results 10 --no-citations
```

To add or refresh citation counts for an existing reading list:

```bash
ai-paper-fetcher citations
ai-paper-fetcher citations --refresh-citations
```

Rank the saved reading list by relevance:

```bash
ai-paper-fetcher rank
```

Fetch ranks automatically by default. To skip that step:

```bash
ai-paper-fetcher fetch --all --max-results 10 --no-rank
```

Generate a Markdown reading list:

```bash
ai-paper-fetcher report
```

Run the full weekly workflow:

```bash
ai-paper-fetcher weekly
```

This fetches all configured topics, pages past duplicates until it finds new papers, enriches citations, downloads PDFs, ranks the reading list, writes `data/reading_list.md`, and writes a dated report to `weekly_reports/YYYY-MM-DD.md`.

To make weekly inspect only the first page of arXiv results per topic:

```bash
ai-paper-fetcher weekly --no-new-results
```

Progress is printed while the tool runs. To hide progress messages:

```bash
ai-paper-fetcher weekly --quiet
```

## Features

- Search arXiv by topic or keyword
- Search configured topics from `config.yaml`
- Keep paging for new papers when earlier results are duplicates
- Restrict configured topics by arXiv categories
- Filter by include and exclude keywords
- Add citation counts from OpenAlex when available
- Rank papers by relevance, recency, citations, and configured keywords
- Generate a Markdown reading report
- Generate dated weekly reports
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
