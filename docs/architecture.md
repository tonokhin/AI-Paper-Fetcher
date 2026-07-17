# Architecture

AI Paper Fetcher is a local-first research library for finding, downloading,
ranking, reading, and organizing papers. It started as a CLI pipeline and now
has three surfaces over the same files:

- CLI commands for fetching, ranking, reporting, progress, recommendations, and
  export.
- A lightweight local browser UI for day-to-day library management.
- A scheduled macOS `launchd` job for daily background fetching.

## Pipeline

```text
config.yaml / foundational_papers.yaml
  -> arXiv metadata fetch
  -> filtering
  -> duplicate tracking
  -> optional OpenAlex citation enrichment
  -> optional PDF download
  -> CSV storage
  -> ranking
  -> Markdown reports
  -> recommendations / UI / curriculum export
```

## Components

| Module | Responsibility |
| --- | --- |
| `cli.py` | Command parsing and workflow orchestration. |
| `arxiv_client.py` | arXiv Atom API search and exact arXiv ID lookup. |
| `config.py` | Topic, track, and foundational-paper YAML loading. |
| `filtering.py` | Include/exclude keyword and date filtering. |
| `citations.py` | OpenAlex citation metadata lookup. |
| `downloader.py` | PDF download and local path assignment. |
| `storage.py` | CSV/JSON read-write, duplicate IDs, schema migration. |
| `ranking.py` | Relevance scoring, priority assignment, sorting. |
| `library.py` | Shared local-library actions, including PDF shelf movement. |
| `progress.py` | Personal learning progress, notes, and next actions. |
| `recommendations.py` | `next` recommendation scoring from rank, citations, and progress. |
| `reporting.py` | Markdown reading-list rendering. |
| `ui.py` | Local browser UI for filtering, notes, progress, PDFs, and logs. |
| `curriculum_export.py` | Export reading-list papers as resource YAML for external learning maps. |

## Data Flow

`weekly` reads configured topics from `config.yaml`, fetches arXiv results,
skips papers already present in `data/seen_papers.json` or
`data/reading_list.csv`, optionally enriches citation counts, optionally
downloads PDFs, ranks the full reading list, and writes reports.

`fetch` can target one ad hoc topic, one configured topic, all configured
topics, or all topics inside a named track.

`foundations` reads exact arXiv IDs from `foundational_papers.yaml`. These
papers are tagged with `collection=foundational`, which gives them a ranking
boost so classic papers are not penalized for being old.

`progress` stores personal learning state separately from the generated reading
list. Updating a paper to `skimmed` or `understood` can also move its local PDF
into the matching shelf.

`next` reads the ranked paper list plus learning progress and recommends what
to read next. It skips `understood` and `archived` papers.

`ui` serves a local-only browser interface over the same CSV/JSON files. It
does not introduce a database or separate state store.

## Tracks And Topics

Research topics live under `topics` in `config.yaml`. Tracks group topic names
so broad learning streams can be fetched and recommended independently.

```text
tracks.ai -> llm_evaluation, ai_agents, interpretability, ...
tracks.fundamentals -> algorithms, mathematics_for_ai
```

Track-aware commands include:

```bash
ai-paper-fetcher fetch --all --track ai
ai-paper-fetcher weekly --track fundamentals
ai-paper-fetcher next --track ai
```

Topics still control the actual arXiv query, keyword filters, and categories.

## Storage

Generated local data is intentionally ignored by git:

```text
data/
papers/
weekly_reports/
logs/
local_tools/
curriculum_mapping.yaml
```

Important local files:

| Path | Purpose |
| --- | --- |
| `data/reading_list.csv` | Main paper metadata store. |
| `data/reading_list.md` | Generated full-library Markdown report. |
| `data/learning_progress.json` | Personal progress, notes, next actions, and understanding levels. |
| `data/seen_papers.json` | Duplicate tracking across fetches. |
| `weekly_reports/YYYY-MM-DD.md` | Dated generated reports from scheduled/daily runs. |
| `logs/weekly.out.log` | Standard output from the scheduled fetch job. |
| `logs/weekly.err.log` | Standard error from the scheduled fetch job. |

The CSV schema is centralized in `models.py`. When fields are added,
`storage.py` migrates existing CSV files by rewriting the header and preserving
old rows.

## PDF Shelves

Downloaded PDFs initially live under their topic folder:

```text
papers/ai_agents/
papers/llm_evaluation/
papers/mathematics_for_ai/
```

Progress updates move PDFs into shelves:

```text
papers/skimmed/<topic>/
papers/read/<topic>/
```

The CSV `local_pdf_path` is updated after a move so reports, recommendations,
and the UI keep linking to the correct file.

## Ranking And Recommendations

The ranker combines:

- configured topic keywords
- high-value terms such as `benchmark`, `evaluation`, `agent`, `reasoning`, and
  `alignment`
- recency
- citation count
- foundational collection status
- exclude keyword penalties

The recommendation layer then combines rank with learning progress:

- skips `understood` and `archived`
- boosts `reading` and `skimmed`
- includes citation count or OpenAlex metadata
- boosts foundational papers
- boosts papers with local PDFs available

The goal is not to perfectly measure paper quality. The goal is to produce a
useful first-pass reading order and keep unfinished learning visible.

## Local UI

The UI is implemented with Python's standard-library HTTP server. It reads and
writes the same files as the CLI.

Main page:

```text
http://localhost:8765/
```

Capabilities:

- filter by track, topic, status, and search text
- paginate the paper list
- update status and understanding
- edit next action
- add notes
- open local PDFs and arXiv PDFs
- show the current recommendation

Logs page:

```text
http://localhost:8765/logs
```

The logs view tails `logs/weekly.out.log` and `logs/weekly.err.log`.

## Scheduling

The macOS `launchd` template lives at:

```text
launchd/com.nokhin.ai-paper-fetcher.weekly.plist
```

The installed user LaunchAgent runs the weekly workflow daily at 08:30. Despite
the command name, daily scheduled runs produce dated reports and act as a daily
paper digest.

## Curriculum Export

`curriculum_export.py` lets the paper library feed an external curriculum graph
or learning map. It maps paper topics to curriculum concept IDs and writes
resource YAML.

The repo includes a committed example mapping:

```text
examples/curriculum_mapping.example.yaml
```

Personal mappings can live at `curriculum_mapping.yaml`, which is ignored by
git.

## External APIs

The project uses:

- arXiv Atom API for paper metadata and PDF links
- OpenAlex Works API for citation counts

OpenAlex matching is conservative. If a title match is not confident, citation
fields are left blank rather than risking bad metadata.

## Design Choices

- CSV and JSON are used before introducing a database.
- PDF downloads are optional.
- Citation enrichment is optional.
- The UI is local-only and dependency-free.
- Daily automation uses `launchd`, while the repo keeps a reusable plist
  template.
- Generated reports and personal learning state stay local by default.
