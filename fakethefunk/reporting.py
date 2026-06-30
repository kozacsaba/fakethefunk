from __future__ import annotations

import csv
from pathlib import Path

from fakethefunk.models import DirectoryResult, FileResult, FileStatus


def write_reports(
    result: DirectoryResult,
    output_dir: Path,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_full_results_csv(result, output_dir / "full_results.csv")
    _write_below_threshold_txt(result, output_dir / "below_threshold.txt")
    _write_errors_txt(result, output_dir / "errors.txt")


def _write_full_results_csv(
    result: DirectoryResult,
    path: Path,
) -> None:
    rows = [_file_result_to_row(r) for r in result.file_results]

    fieldnames = [
        "path",
        "status",
        "sample_rate",
        "duration_seconds",
        "block_count",
        "reference_power_db",
        "high_power_db",
        "ratio_db",
        "high_max_db",
        "block_ratio_min_db",
        "block_ratio_mean_db",
        "block_ratio_median_db",
        "block_ratio_p95_db",
        "block_ratio_max_db",
        "passed_threshold",
        "error_message",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_below_threshold_txt(
    result: DirectoryResult,
    path: Path,
) -> None:
    with path.open("w", encoding="utf-8") as file:
        for item in result.below_threshold_files:
            file.write(str(item.path) + "\n")


def _write_errors_txt(
    result: DirectoryResult,
    path: Path,
) -> None:
    with path.open("w", encoding="utf-8") as file:
        for item in result.skipped_or_failed_files:
            file.write(f"{item.status.value}: {item.path}")

            if item.error_message:
                file.write(f" -- {item.error_message}")

            file.write("\n")


def _file_result_to_row(result: FileResult) -> dict[str, object]:
    analysis = result.analysis

    return {
        "path": str(result.path),
        "status": result.status.value,
        "sample_rate": result.sample_rate,
        "duration_seconds": result.duration_seconds,

        "block_count": None if analysis is None else analysis.block_count,
        "reference_power_db": None if analysis is None else analysis.reference_power_db,
        "high_power_db": None if analysis is None else analysis.high_power_db,
        "ratio_db": None if analysis is None else analysis.ratio_db,
        "high_max_db": None if analysis is None else analysis.high_max_db,

        "block_ratio_min_db": None if analysis is None else analysis.block_ratio_min_db,
        "block_ratio_mean_db": None if analysis is None else analysis.block_ratio_mean_db,
        "block_ratio_median_db": None if analysis is None else analysis.block_ratio_median_db,
        "block_ratio_p95_db": None if analysis is None else analysis.block_ratio_p95_db,
        "block_ratio_max_db": None if analysis is None else analysis.block_ratio_max_db,

        "passed_threshold": None if analysis is None else analysis.passed_threshold,
        "error_message": result.error_message,
    }
