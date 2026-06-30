from __future__ import annotations

import argparse
from pathlib import Path

from audio_analyzer.config import AnalysisConfig
from audio_analyzer.directory_processor import process_directory
from audio_analyzer.reporting import write_reports


def main() -> int:
    args = _parse_args()

    config = AnalysisConfig(
        reference_min_hz=args.reference_min_hz,
        reference_max_hz=args.reference_max_hz,
        high_min_hz=args.high_min_hz,
        high_max_hz=args.high_max_hz,
        min_sample_rate_hz=args.min_sample_rate_hz,
        block_size=args.block_size,
        ratio_threshold_db=args.ratio_threshold_db,
    )

    result = process_directory(args.input_path, config)
    write_reports(result, args.output_dir)

    print(f"Processed files: {len(result.file_results)}")
    print(f"OK files: {len(result.ok_files)}")
    print(f"Skipped/failed files: {len(result.skipped_or_failed_files)}")

    if args.ratio_threshold_db is not None:
        print(f"Below threshold: {len(result.below_threshold_files)}")
    else:
        print("No threshold was set; below_threshold.txt will be empty.")

    print(f"Output dir: {args.output_dir}")

    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input_path",
        type=Path,
        help="Directory to crawl recursively.",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("audio_analysis_output"),
        help="Output directory.",
    )

    parser.add_argument(
        "--ratio-threshold-db",
        type=float,
        default=None,
        help="Optional threshold for high-band/reference-band ratio in dB.",
    )

    parser.add_argument("--block-size", type=int, default=16_384)

    parser.add_argument("--reference-min-hz", type=float, default=20.0)
    parser.add_argument("--reference-max-hz", type=float, default=17_000.0)

    parser.add_argument("--high-min-hz", type=float, default=17_000.0)
    parser.add_argument("--high-max-hz", type=float, default=20_000.0)

    parser.add_argument("--min-sample-rate-hz", type=int, default=41_000)

    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
