#!/usr/bin/env python3
"""
Resize image files for use as animation frames.

Examples:
  python resize_frames.py --input . --output frames_small --max-width 640 --max-height 360
  python resize_frames.py --input raw_frames --output frames_half --scale 0.5
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize a folder of image frames for animation use."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input folder containing image frames.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output folder for resized image frames.",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=640,
        help="Maximum width in pixels (used with --max-height). Default: 640",
    )
    parser.add_argument(
        "--max-height",
        type=int,
        default=360,
        help="Maximum height in pixels (used with --max-width). Default: 360",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Optional scale factor (e.g. 0.5 for 50%% size). If set, overrides max dimensions.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    return parser.parse_args()


def iter_images(input_dir: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
    )


def resized_size(
    width: int, height: int, max_width: int, max_height: int, scale: float | None
) -> tuple[int, int]:
    if scale is not None:
        if scale <= 0:
            raise ValueError("--scale must be greater than 0.")
        new_w = max(1, int(round(width * scale)))
        new_h = max(1, int(round(height * scale)))
        return new_w, new_h

    ratio = min(max_width / width, max_height / height, 1.0)
    new_w = max(1, int(round(width * ratio)))
    new_h = max(1, int(round(height * ratio)))
    return new_w, new_h


def main() -> None:
    args = parse_args()

    if not args.input.exists() or not args.input.is_dir():
        raise SystemExit(f"Input directory not found: {args.input}")

    args.output.mkdir(parents=True, exist_ok=True)
    images = iter_images(args.input)

    if not images:
        raise SystemExit(
            f"No supported image files found in {args.input}. "
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    count = 0
    for image_path in images:
        out_path = args.output / image_path.name
        if out_path.exists() and not args.overwrite:
            continue

        with Image.open(image_path) as img:
            new_size = resized_size(
                img.width, img.height, args.max_width, args.max_height, args.scale
            )
            if new_size != img.size:
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            img.save(out_path)
            count += 1
            print(f"Saved: {out_path} ({new_size[0]}x{new_size[1]})")

    print(f"\nDone. Wrote {count} resized frame(s) to: {args.output}")


if __name__ == "__main__":
    main()
