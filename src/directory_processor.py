from __future__ import annotations

from pathlib import Path

from audio_analyzer.config import AnalysisConfig
from audio_analyzer.file_processor import process_file
from audio_analyzer.models import DirectoryResult


def process_directory(
    root_path: Path,
    config: AnalysisConfig,
) -> DirectoryResult:
    root_path = Path(root_path)

    if not root_path.exists():
        raise FileNotFoundError(root_path)

    if not root_path.is_dir():
        raise NotADirectoryError(root_path)

    results = []

    for path in sorted(root_path.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in config.supported_extensions:
            continue

        results.append(process_file(path, config))

    return DirectoryResult(
        root_path=root_path,
        file_results=results,
    )
