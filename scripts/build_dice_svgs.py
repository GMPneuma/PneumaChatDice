"""Package the detailed D10 artwork as transparent PNGs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


FACES = [*(str(value) for value in range(1, 11)), "skull", "flame"]


def convex_hull(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(origin, a, b):
        return (a[0] - origin[0]) * (b[1] - origin[1]) - (a[1] - origin[1]) * (b[0] - origin[0])

    lower: list[tuple[int, int]] = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[tuple[int, int]] = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def actual_die_alpha(image: Image.Image) -> Image.Image:
    """Derive alpha from the generated die's own convex silhouette."""
    rgba = image.convert("RGBA")
    existing_alpha = np.asarray(rgba.getchannel("A"))

    # Preserve genuine generated transparency when it already exists.
    if existing_alpha[0, 0] < 16 and np.count_nonzero(existing_alpha < 16) > existing_alpha.size // 20:
        return rgba

    rgb = np.asarray(rgba)[:, :, :3].astype(np.int16)
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    saturation = maximum - minimum
    border = np.concatenate((maximum[0], maximum[-1], maximum[:, 0], maximum[:, -1]))
    dark_background = float(np.median(border)) < 80

    if dark_background:
        foreground = (saturation > 22) | (maximum > 48)
    else:
        # Some generated sources contain a baked gray checkerboard. Select
        # colored pixels plus the genuinely dark die body without admitting
        # either shade of the neutral checker pattern into the silhouette.
        foreground = (saturation > 22) | (minimum < 90)

    ys, xs = np.nonzero(foreground)
    if len(xs) < 100:
        raise ValueError("Could not identify the die silhouette")

    # Extreme coordinates are sufficient for an accurate convex hull and avoid
    # feeding more than a million interior pixels to the hull algorithm.
    boundary: list[tuple[int, int]] = []
    for y in range(0, rgba.height, 2):
        row = xs[ys == y]
        if row.size:
            boundary.extend(((int(row.min()), y), (int(row.max()), y)))
    for x in range(0, rgba.width, 2):
        column = ys[xs == x]
        if column.size:
            boundary.extend(((x, int(column.min())), (x, int(column.max()))))

    hull = convex_hull(boundary)
    mask = Image.new("L", rgba.size, 0)
    ImageDraw.Draw(mask).polygon(hull, fill=255)
    # Contract the hull by one source pixel before antialiasing. Expanding it
    # exposes the light checkerboard fringe baked into several generated faces.
    mask = mask.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.GaussianBlur(0.3))
    # Resampling/blur can leave a nearly invisible alpha value on the outermost
    # pixel. Foundry never needs content this close to the canvas boundary.
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle((0, 0, rgba.width - 1, 1), fill=0)
    mask_draw.rectangle((0, rgba.height - 2, rgba.width - 1, rgba.height - 1), fill=0)
    mask_draw.rectangle((0, 0, 1, rgba.height - 1), fill=0)
    mask_draw.rectangle((rgba.width - 2, 0, rgba.width - 1, rgba.height - 1), fill=0)
    rgba.putalpha(mask)
    return rgba


def package_face(source: Path, destination: Path, face_name: str) -> None:
    with Image.open(source) as source_image:
        face = actual_die_alpha(source_image).resize((850, 850), Image.Resampling.LANCZOS)
        face_alpha = face.getchannel("A")
        face_alpha_draw = ImageDraw.Draw(face_alpha)
        face_alpha_draw.rectangle((0, 0, face.width - 1, 1), fill=0)
        face_alpha_draw.rectangle((0, face.height - 2, face.width - 1, face.height - 1), fill=0)
        face_alpha_draw.rectangle((0, 0, 1, face.height - 1), fill=0)
        face_alpha_draw.rectangle((face.width - 2, 0, face.width - 1, face.height - 1), fill=0)
        face.putalpha(face_alpha)

        destination.mkdir(parents=True, exist_ok=True)
        png_name = f"d10_{face_name}.png"

        png_path = destination / png_name
        face.save(png_path, format="PNG", optimize=True)

def package_set(
    source_root: Path,
    source_prefix: str,
    destination: Path,
    source_aliases: dict[str, str] | None = None,
) -> None:
    source_aliases = source_aliases or {}
    for face in FACES:
        source_face = source_aliases.get(face, face)
        source_face = f"{int(source_face):02d}" if source_face.isdigit() else source_face
        package_face(source_root / f"{source_prefix}-{source_face}.png", destination, face)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    package_set(
        args.generated_root / "red-blue",
        "red-blue",
        args.output_root / "red-blue",
        # The two original generated source files were named in reverse.
        source_aliases={"skull": "flame", "flame": "skull"},
    )
    package_set(
        args.generated_root / "purple-green",
        "purple-green",
        args.output_root / "purple-green",
    )


if __name__ == "__main__":
    main()
