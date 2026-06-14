# Architecture

AI Paper Fetcher is a CLI-first Python application. It is organized as a small pipeline where each stage handles one part of the research workflow.

## Pipeline

```text
config.yaml / foundational_papers.yaml
  -> arXiv metadata fetch
  -> filtering
  -> duplicate tracking
  -> OpenAlex citation enrichment
  -> optional PDF download
  -> CSV storage
  -> ranking
  -> Markdown reports
```

## Components

| Module | Responsibility |
| --- | --- |
| `cli.py` | Command parsing and workflow orchestration. |
| `arxiv_client.py` | arXiv Atom API search and exact arXiv ID lookup. |
| `config.py` | Topic and foundational-paper YAML loading. |
| `filtering.py` | Include/exclude keyword and date filtering. |
| `citations.py` | OpenAlex citation metadata lookup. |
| `downloader.py` | PDF download and local path assignment. |
| `storage.py` | CSV/JSON read-write, duplicate IDs, schema migration. |
| `ranking.py` | Relevance scoring, priority assignment, sorting. |
| `reporting.py` | Markdown reading-list rendering. |

## Data Flow

`weekly` reads configured topics from `config.yaml`, fetches arXiv results, skips papers already present in `data/seen_papers.json` or `data/reading_list.csv`, optionally enriches citation counts, optionally downloads PDFs, ranks the full reading list, and writes reports.

`foundations` reads exact arXiv IDs from `foundational_papers.yaml`. These papers are tagged with `collection=foundational`, which gives them a ranking boost so classic papers are not penalized for being old.

## Storage

Generated local data is intentionally ignored by git:

```text
data/reading_list.csv
data/reading_list.md
data/seen_papers.json
papers/
weekly_reports/
```

The CSV schema is centralized in `models.py`. When new fields are added, `storage.py` migrates existing CSV files by rewriting the header and preserving old rows.

## Ranking Signals

The ranker combines:

- configured topic keywords
- high-value terms such as `benchmark`, `evaluation`, `agent`, `reasoning`, and `alignment`
- recency
- citation count
- foundational collection status
- exclude keyword penalties

The goal is not to perfectly measure paper quality. The goal is to produce a useful first-pass reading order.

## External APIs

The project uses:

- arXiv Atom API for paper metadata and PDF links
- OpenAlex Works API for citation counts

OpenAlex matching is conservative. If a title match is not confident, citation fields are left blank rather than risking bad metadata.

## Design Choices

- CSV and JSON are used before introducing a database.
- PDF downloads are optional.
- Citation enrichment is optional.
- Weekly runs can use `--fast` for a quick metadata-only scan.
- Generated reports are local by default, while `examples/` contains committed sample output.
