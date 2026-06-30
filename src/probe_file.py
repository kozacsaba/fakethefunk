from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from audio_analyzer.audio_io import load_audio
from audio_analyzer.config import AnalysisConfig
from audio_analyzer.spectral_analysis import (
    analyze_audio,
    compute_block_power_spectra,
    linear_power_to_db,
)


def main() -> int:
    args = _parse_args()

    config = AnalysisConfig(
        reference_min_hz=args.reference_min_hz,
        reference_max_hz=args.reference_max_hz,
        high_min_hz=args.high_min_hz,
        high_max_hz=args.high_max_hz,
        min_sample_rate_hz=args.min_sample_rate_hz,
        block_size=args.block_size,
    )

    audio = load_audio(args.audio_file)

    if audio.sample_rate < config.min_sample_rate_hz:
        print(f"SKIPPED: sample rate is {audio.sample_rate} Hz")
        print(f"Required minimum: {config.min_sample_rate_hz} Hz")
        return 1

    frames = compute_block_power_spectra(audio, config)
    analysis = analyze_audio(audio, config)

    _print_stats(args.audio_file, audio.sample_rate, audio.duration_seconds, analysis)
    _plot_probe(args.audio_file, frames, config, args.max_plot_hz, args.save_plot)

    if not args.no_show:
        plt.show()

    return 0


def _print_stats(
    path: Path,
    sample_rate: int,
    duration_seconds: float,
    analysis,
) -> None:
    print(f"File: {path}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Duration: {duration_seconds:.2f} s")
    print(f"Blocks: {analysis.block_count}")
    print()
    print(f"Reference power dB: {analysis.reference_power_db:.2f}")
    print(f"High-band power dB: {analysis.high_power_db:.2f}")
    print(f"High/reference ratio dB: {analysis.ratio_db:.2f}")
    print(f"High-band max dB: {analysis.high_max_db:.2f}")
    print()
    print("Per-block high/reference ratio dB:")
    print(f"  min:    {analysis.block_ratio_min_db:.2f}")
    print(f"  mean:   {analysis.block_ratio_mean_db:.2f}")
    print(f"  median: {analysis.block_ratio_median_db:.2f}")
    print(f"  p95:    {analysis.block_ratio_p95_db:.2f}")
    print(f"  max:    {analysis.block_ratio_max_db:.2f}")


def _plot_probe(
    path: Path,
    frames,
    config: AnalysisConfig,
    max_plot_hz: float,
    save_plot: Path | None,
) -> None:
    freq_mask = frames.freqs <= max_plot_hz

    spectrogram_db = linear_power_to_db(frames.power[:, freq_mask]).T
    freqs = frames.freqs[freq_mask]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].imshow(
        spectrogram_db,
        origin="lower",
        aspect="auto",
        extent=[
            frames.times[0],
            frames.times[-1],
            freqs[0],
            freqs[-1],
        ],
    )

    axes[0].set_title(f"Spectrogram: {path.name}")
    axes[0].set_xlabel("Time [s]")
    axes[0].set_ylabel("Frequency [Hz]")
    axes[0].axhline(config.high_min_hz, linestyle="--")
    axes[0].axhline(config.high_max_hz, linestyle="--")

    mean_spectrum_db = linear_power_to_db(np.mean(frames.power, axis=0))

    axes[1].plot(frames.freqs[freq_mask], mean_spectrum_db[freq_mask])
    axes[1].set_title("Mean spectrum")
    axes[1].set_xlabel("Frequency [Hz]")
    axes[1].set_ylabel("Power [dB]")
    axes[1].axvline(config.high_min_hz, linestyle="--")
    axes[1].axvline(config.high_max_hz, linestyle="--")

    fig.tight_layout()

    if save_plot is not None:
        fig.savefig(save_plot, dpi=150)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("audio_file", type=Path)

    parser.add_argument("--block-size", type=int, default=16_384)

    parser.add_argument("--reference-min-hz", type=float, default=20.0)
    parser.add_argument("--reference-max-hz", type=float, default=17_000.0)

    parser.add_argument("--high-min-hz", type=float, default=17_000.0)
    parser.add_argument("--high-max-hz", type=float, default=20_000.0)

    parser.add_argument("--min-sample-rate-hz", type=int, default=41_000)
    parser.add_argument("--max-plot-hz", type=float, default=22_000.0)

    parser.add_argument("--save-plot", type=Path, default=None)
    parser.add_argument("--no-show", action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
