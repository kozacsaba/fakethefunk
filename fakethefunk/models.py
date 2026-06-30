from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np


class FileStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    SKIPPED_LOW_SAMPLE_RATE = "skipped_low_sample_rate"
    DECODE_ERROR = "decode_error"
    ANALYSIS_ERROR = "analysis_error"


@dataclass(frozen=True)
class AudioData:
    samples: np.ndarray
    sample_rate: int
    duration_seconds: float


@dataclass(frozen=True)
class SpectralFrames:
    freqs: np.ndarray
    times: np.ndarray
    power: np.ndarray


@dataclass(frozen=True)
class AnalysisResult:
    block_count: int

    reference_power: float
    high_power: float

    reference_power_db: float
    high_power_db: float
    ratio_db: float

    high_max_db: float

    block_ratio_min_db: float
    block_ratio_mean_db: float
    block_ratio_median_db: float
    block_ratio_p95_db: float
    block_ratio_max_db: float

    passed_threshold: bool | None


@dataclass(frozen=True)
class FileResult:
    path: Path
    status: FileStatus

    sample_rate: int | None = None
    duration_seconds: float | None = None
    analysis: AnalysisResult | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class DirectoryResult:
    root_path: Path
    file_results: list[FileResult]

    @property
    def ok_files(self) -> list[FileResult]:
        return [r for r in self.file_results if r.status == FileStatus.OK]

    @property
    def below_threshold_files(self) -> list[FileResult]:
        return [
            r for r in self.file_results
            if r.analysis is not None and r.analysis.passed_threshold is False
        ]

    @property
    def skipped_or_failed_files(self) -> list[FileResult]:
        return [r for r in self.file_results if r.status != FileStatus.OK]
        