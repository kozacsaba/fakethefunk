from __future__ import annotations

import numpy as np

from audio_analyzer.config import AnalysisConfig
from audio_analyzer.models import AnalysisResult, AudioData, SpectralFrames

_EPS = 1e-300


def linear_power_to_db(value: float | np.ndarray) -> float | np.ndarray:
    return 10.0 * np.log10(np.maximum(value, _EPS))


def compute_block_power_spectra(
    audio: AudioData,
    config: AnalysisConfig,
) -> SpectralFrames:
    samples = np.asarray(audio.samples, dtype=np.float64)

    if samples.ndim != 1:
        raise ValueError("Expected mono audio.")

    if len(samples) == 0:
        raise ValueError("Audio contains no samples.")

    blocks = _split_into_blocks(samples, config.block_size)
    window = _make_window(config.window, config.block_size)

    windowed = blocks * window[None, :]
    spectrum = np.fft.rfft(windowed, axis=1)
    power = np.square(np.abs(spectrum))

    freqs = np.fft.rfftfreq(config.block_size, d=1.0 / audio.sample_rate)
    times = np.arange(power.shape[0]) * (config.block_size / audio.sample_rate)

    return SpectralFrames(
        freqs=freqs,
        times=times,
        power=power,
    )


def analyze_audio(
    audio: AudioData,
    config: AnalysisConfig,
) -> AnalysisResult:
    frames = compute_block_power_spectra(audio, config)

    reference_block_power = _band_mean_power_per_block(
        frames,
        config.reference_min_hz,
        config.reference_max_hz,
    )

    high_block_power = _band_mean_power_per_block(
        frames,
        config.high_min_hz,
        config.high_max_hz,
    )

    reference_power = float(np.mean(reference_block_power))
    high_power = float(np.mean(high_block_power))

    reference_power_db = float(linear_power_to_db(reference_power))
    high_power_db = float(linear_power_to_db(high_power))
    ratio_db = float(linear_power_to_db(high_power / max(reference_power, _EPS)))

    block_ratios_db = linear_power_to_db(
        high_block_power / np.maximum(reference_block_power, _EPS)
    )

    high_band_mask = _band_mask(
        frames.freqs,
        config.high_min_hz,
        config.high_max_hz,
    )

    high_max_db = float(linear_power_to_db(np.max(frames.power[:, high_band_mask])))

    passed_threshold = None
    if config.ratio_threshold_db is not None:
        passed_threshold = ratio_db >= config.ratio_threshold_db

    return AnalysisResult(
        block_count=int(frames.power.shape[0]),

        reference_power=reference_power,
        high_power=high_power,

        reference_power_db=reference_power_db,
        high_power_db=high_power_db,
        ratio_db=ratio_db,

        high_max_db=high_max_db,

        block_ratio_min_db=float(np.min(block_ratios_db)),
        block_ratio_mean_db=float(np.mean(block_ratios_db)),
        block_ratio_median_db=float(np.median(block_ratios_db)),
        block_ratio_p95_db=float(np.percentile(block_ratios_db, 95)),
        block_ratio_max_db=float(np.max(block_ratios_db)),

        passed_threshold=passed_threshold,
    )


def _split_into_blocks(samples: np.ndarray, block_size: int) -> np.ndarray:
    if block_size <= 0:
        raise ValueError("Block size must be positive.")

    full_block_count = len(samples) // block_size

    if full_block_count == 0:
        padded = np.zeros(block_size, dtype=np.float64)
        padded[:len(samples)] = samples
        return padded.reshape(1, block_size)

    usable = samples[:full_block_count * block_size]
    return usable.reshape(full_block_count, block_size)


def _make_window(name: str, block_size: int) -> np.ndarray:
    if name == "hann":
        return np.hanning(block_size)

    if name == "rect":
        return np.ones(block_size, dtype=np.float64)

    raise ValueError(f"Unsupported window type: {name}")


def _band_mask(
    freqs: np.ndarray,
    min_hz: float,
    max_hz: float,
) -> np.ndarray:
    mask = (freqs >= min_hz) & (freqs < max_hz)

    if not np.any(mask):
        raise ValueError(f"No FFT bins found for band {min_hz:g}-{max_hz:g} Hz.")

    return mask


def _band_mean_power_per_block(
    frames: SpectralFrames,
    min_hz: float,
    max_hz: float,
) -> np.ndarray:
    mask = _band_mask(frames.freqs, min_hz, max_hz)
    return np.mean(frames.power[:, mask], axis=1)
