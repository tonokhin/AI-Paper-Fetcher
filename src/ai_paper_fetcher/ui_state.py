from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class UiState:
    data_dir: Path
    papers_dir: Path
    config_path: Path
    logs_dir: Path
