# AI Paper Fetcher

AI Paper Fetcher is a command-line research assistant for finding, organizing, ranking, and reporting on AI papers from arXiv.

It supports two complementary workflows:

- `weekly`: find new papers from configured research topics.
- `foundations`: import classic papers from a curated foundational reading list.

The tool stores local metadata, skips duplicates, enriches citation counts with OpenAlex, ranks papers by relevance, downloads PDFs when requested, and generates Markdown reading reports.

## Quick Start

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/ai-paper-fetcher weekly --fast
```

Fast mode is a metadata-only weekly run:

```text
max-results 3
max-pages 2
no PDF downloads
no citation lookups
```

## Main Workflows

Run the weekly research feed:

```bash
.venv/bin/ai-paper-fetcher weekly --max-results 10
```

Import foundational AI papers:

```bash
.venv/bin/ai-paper-fetcher foundations --no-download --no-citations
```

Generate a Markdown report from the current reading list:

```bash
.venv/bin/ai-paper-fetcher report
```

Download PDFs later for papers that were previously saved with `--no-download`:

```bash
.venv/bin/ai-paper-fetcher download-missing
```

Track your learning progress:

```bash
.venv/bin/ai-paper-fetcher next
.venv/bin/ai-paper-fetcher progress next
.venv/bin/ai-paper-fetcher progress update 2606.14027 --status reading --understanding 2 --next-action "Read the experiments section"
.venv/bin/ai-paper-fetcher progress note 2606.14027 "The threat model is the key idea."
```

## Outputs

Generated outputs stay local and are ignored by git:

```text
data/reading_list.csv
data/reading_list.md
data/learning_progress.json
data/seen_papers.json
papers/
weekly_reports/YYYY-MM-DD.md
```

See [examples/sample_reading_list.md](examples/sample_reading_list.md) for a small committed example of the report format.

## Commands

| Command | Purpose |
| --- | --- |
| `weekly` | Fetch all configured topics, rank, and generate reports. |
| `foundations` | Import classic papers from `foundational_papers.yaml`. |
| `fetch` | Fetch one ad hoc topic, one configured topic, or all topics. |
| `citations` | Refresh OpenAlex citation counts for saved papers. |
| `rank` | Re-rank the current CSV reading list. |
| `report` | Regenerate the Markdown reading list. |
| `download-missing` | Download PDFs for existing rows with missing local files. |
| `progress` | Track reading status, understanding, notes, and next actions. |
| `next` | Recommend the next paper to read from progress, ranking, and citation signals. |

## Examples

Fetch one configured topic:

```bash
.venv/bin/ai-paper-fetcher fetch --config-topic llm_evaluation --max-results 10
```

Fetch all configured topics:

```bash
.venv/bin/ai-paper-fetcher fetch --all --max-results 10
```

Keep paging until enough new papers are found:

```bash
.venv/bin/ai-paper-fetcher fetch --config-topic llm_evaluation --max-results 10 --new-results --max-pages 5
```

Run weekly without slow network enrichments:

```bash
.venv/bin/ai-paper-fetcher weekly --fast
```

Run weekly but inspect only the first arXiv page per topic:

```bash
.venv/bin/ai-paper-fetcher weekly --no-new-results
```

Hide progress messages:

```bash
.venv/bin/ai-paper-fetcher weekly --quiet
```

## Learning Progress

Learning progress is stored separately from the generated reading list in `data/learning_progress.json`, so daily fetches, ranking, and report regeneration do not overwrite your personal notes.

Useful commands:

```bash
.venv/bin/ai-paper-fetcher next
.venv/bin/ai-paper-fetcher next --limit 3
.venv/bin/ai-paper-fetcher progress next --limit 5
.venv/bin/ai-paper-fetcher progress list
.venv/bin/ai-paper-fetcher progress show 2606.14027
.venv/bin/ai-paper-fetcher progress update 2606.14027 --status skimmed --understanding 1
.venv/bin/ai-paper-fetcher progress update 2606.14027 --minutes 25 --next-action "Summarize the method"
.venv/bin/ai-paper-fetcher progress update 2606.14027 --status understood
.venv/bin/ai-paper-fetcher progress note 2606.14027 "Agent-induced data flow is the central security concern."
```

Supported statuses are `queued`, `skimmed`, `reading`, `understood`, and `archived`. Understanding is tracked on a `0` to `5` scale, where `5` means you can explain the paper to someone else. Markdown reports include saved progress under each paper.

When a paper with a local PDF is marked `understood`, the PDF is moved into `papers/read/` and the reading-list CSV is updated with the new path. This keeps completed papers out of the active topic folders without losing the file link.

The top-level `next` command skips papers marked `understood` or `archived`, boosts papers already in progress, and uses relevance score, citation count/OpenAlex metadata, foundational status, and local PDF availability to explain why a paper is recommended.

## Configuration

Research topics live in [config.yaml](config.yaml).

Each topic can define:

- arXiv search query
- include keywords
- exclude keywords
- arXiv categories
- optional date filters

Foundational papers live in [foundational_papers.yaml](foundational_papers.yaml). Entries are fetched by exact arXiv ID and tagged as `collection=foundational`.

## Features

- Search arXiv by topic or keyword.
- Search configured topics from `config.yaml`.
- Import curated foundational papers from `foundational_papers.yaml`.
- Page past duplicates when looking for new papers.
- Filter by arXiv categories and keywords.
- Track seen papers across runs.
- Enrich citation counts from OpenAlex when available.
- Download PDFs into topic-specific folders.
- Backfill missing PDFs after metadata-only runs.
- Rank by topic relevance, high-value research terms, recency, citation count, and foundational status.
- Generate Markdown reading reports.
- Generate dated weekly reports.
- Print progress during long runs.

## Architecture

See [docs/architecture.md](docs/architecture.md).

At a high level:

```text
arXiv -> filters -> duplicate tracking -> OpenAlex citations -> PDF storage -> ranking -> Markdown reports
```

## Development

Run tests:

```bash
.venv/bin/python -m unittest discover -s tests
```
