from __future__ import annotations

from pathlib import Path

from audio_analyzer.audio_io import load_audio
from audio_analyzer.config import AnalysisConfig
from audio_analyzer.models import FileResult, FileStatus
from audio_analyzer.spectral_analysis import analyze_audio


def process_file(
    path: Path,
    config: AnalysisConfig,
) -> FileResult:
    path = Path(path)

    if path.suffix.lower() not in config.supported_extensions:
        return FileResult(
            path=path,
            status=FileStatus.UNSUPPORTED,
            error_message="Unsupported file extension.",
        )

    try:
        audio = load_audio(path)
    except Exception as exc:
        return FileResult(
            path=path,
            status=FileStatus.DECODE_ERROR,
            error_message=str(exc),
        )

    if audio.sample_rate < config.min_sample_rate_hz:
        return FileResult(
            path=path,
            status=FileStatus.SKIPPED_LOW_SAMPLE_RATE,
            sample_rate=audio.sample_rate,
            duration_seconds=audio.duration_seconds,
            error_message=(
                f"Sample rate {audio.sample_rate} Hz is below "
                f"{config.min_sample_rate_hz} Hz."
            ),
        )

    try:
        analysis = analyze_audio(audio, config)
    except Exception as exc:
        return FileResult(
            path=path,
            status=FileStatus.ANALYSIS_ERROR,
            sample_rate=audio.sample_rate,
            duration_seconds=audio.duration_seconds,
            error_message=str(exc),
        )

    return FileResult(
        path=path,
        status=FileStatus.OK,
        sample_rate=audio.sample_rate,
        duration_seconds=audio.duration_seconds,
        analysis=analysis,
    )
