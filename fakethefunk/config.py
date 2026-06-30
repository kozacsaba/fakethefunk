from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisConfig:
    reference_min_hz: float = 20.0
    reference_max_hz: float = 17_000.0
    high_min_hz: float = 17_000.0
    high_max_hz: float = 20_000.0

    min_sample_rate_hz: int = 41_000

    block_size: int = 16_384
    window: str = "hann"

    ratio_threshold_db: float | None = None

    supported_extensions: tuple[str, ...] = (
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
    )
    