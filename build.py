#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "soundfile",
#   "numpy",
#   "scipy",
# ]
# ///

from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
from scipy.signal import resample
import soundfile as sf
import numpy as np
import tempfile

DATA = Path(".data")
ARCHIVE = DATA / "AKWF.zip"
EXTRACTED = DATA / ".AKWF-extracted"

URL = "http://www.adventurekid.se/AKRTfiles/AKWF/AKWF.zip"

DATA.mkdir(exist_ok=True)

# Download
if not ARCHIVE.exists():
    print("Downloading AKWF...")
    with tempfile.NamedTemporaryFile(dir=DATA, delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        urlretrieve(URL, tmp_path)
        tmp_path.replace(ARCHIVE)
    finally:
        tmp_path.unlink(missing_ok=True)

# Extract
if not EXTRACTED.exists():
    print("Extracting AKWF...")

    with ZipFile(ARCHIVE) as z:
        for member in z.infolist():
            target = (DATA / member.filename).resolve()
            if not target.is_relative_to(DATA.resolve()):
                raise ValueError("Unsafe ZIP entry: " + member.filename)

        z.extractall(DATA)

    EXTRACTED.touch()

# Patch known mono files in the stereo folder
for name in (
    "AKWF_stereo_0108.wav",
    "AKWF_stereo_0109.wav",
    "AKWF_stereo_0110.wav",
):
    path = DATA / "AKWF_stereo" / name

    audio, sr = sf.read(path)

    if audio.ndim == 1:
        audio = np.column_stack((audio, audio))
        sf.write(path, audio, sr)
        print(f"Patched to stereo: {path}")

# Generate wavetables
for folder in sorted(DATA.iterdir()):
    if not folder.is_dir() or folder.name.startswith("."):
        continue

    name = folder.name.replace("AKWF_00", "wt_").replace("AKWF_", "wt_")
    output_dir = Path(name)
    output_dir.mkdir(exist_ok=True)
    output = output_dir / (name + ".wav")

    chunks = []
    sr = None
    channels = None
    first_file = None

    for path in sorted(folder.glob("*.wav")):
        audio, file_sr = sf.read(path)
        if sr is None:
            sr = file_sr
            channels = audio.ndim
            first_file = path
        else:
            if file_sr != sr:
                raise ValueError(
                    f"Sample rate mismatch:\n"
                    f"  First: {first_file} ({sr} Hz)\n"
                    f"  Found: {path} ({file_sr} Hz)"
                )

            if audio.ndim != channels:
                raise ValueError(
                    f"Channel layout mismatch:\n"
                    f"  First: {first_file} ({channels} dimensions, "
                    f"shape {chunks[0].shape})\n"
                    f"  Found: {path} ({audio.ndim} dimensions, "
                    f"shape {audio.shape})"
                )

        chunks.append(resample(audio, 2048, axis=0))

    if not chunks:
        continue

    wavetable = np.concatenate(chunks, axis=0)
    sf.write(output, wavetable, sr)

    print(f"{output}: {len(chunks)} frames, {len(wavetable)} samples")

