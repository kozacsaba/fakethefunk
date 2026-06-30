from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from fakethefunk.models import AudioData


def load_audio(path: Path) -> AudioData:
    samples, sample_rate = librosa.load(
        path,
        sr=None,
        mono=True,
    )

    samples = np.asarray(samples, dtype=np.float64)
    duration_seconds = float(len(samples) / sample_rate)

    return AudioData(
        samples=samples,
        sample_rate=int(sample_rate),
        duration_seconds=duration_seconds,
    )
