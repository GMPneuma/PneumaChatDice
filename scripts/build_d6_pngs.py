"""Build the detailed D6 WebP set with genuine transparent backgrounds."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from build_dice_svgs import OUTPUT_SIZE, actual_die_alpha, save_webp


COMPOSE_SIZE = 850
D6_MARGIN = 16
D6_VISIBLE_SIZE = OUTPUT_SIZE - 2 * D6_MARGIN


def largest_component(mask: np.ndarray) -> np.ndarray:
    """Return only the largest four-connected component in a boolean mask."""
    remaining = mask.copy()
    best: list[tuple[int, int]] = []

    while remaining.any():
        start_y, start_x = (int(value) for value in np.argwhere(remaining)[0])
        stack = [(start_y, start_x)]
        remaining[start_y, start_x] = False
        component: list[tuple[int, int]] = []

        while stack:
            y, x = stack.pop()
            component.append((y, x))
            for next_y, next_x in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if (
                    0 <= next_y < mask.shape[0]
                    and 0 <= next_x < mask.shape[1]
                    and remaining[next_y, next_x]
                ):
                    remaining[next_y, next_x] = False
                    stack.append((next_y, next_x))

        if len(component) > len(best):
            best = component

    selected = np.zeros_like(mask)
    if best:
        ys, xs = zip(*best)
        selected[np.asarray(ys), np.asarray(xs)] = True
    return selected


def clean_die(source: Path) -> Image.Image:
    with Image.open(source) as source_image:
        cleaned = actual_die_alpha(source_image)
    cleaned = cleaned.resize((COMPOSE_SIZE, COMPOSE_SIZE), Image.Resampling.LANCZOS)

    # Lanczos can introduce extremely faint alpha ringing at the canvas edge.
    alpha = np.asarray(cleaned.getchannel("A")).copy()
    alpha[:2, :] = 0
    alpha[-2:, :] = 0
    alpha[:, :2] = 0
    alpha[:, -2:] = 0
    cleaned.putalpha(Image.fromarray(alpha, mode="L"))
    return cleaned


def normalize_d6_canvas(image: Image.Image) -> Image.Image:
    """Fit the visible die to a shared tight square so every D6 renders equally."""
    rgba = image.convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"))
    ys, xs = np.nonzero(alpha >= 16)
    if len(xs) < 100:
        raise ValueError("Could not identify the visible D6 bounds")

    bounds = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    fitted = rgba.crop(bounds).resize(
        (D6_VISIBLE_SIZE, D6_VISIBLE_SIZE),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (OUTPUT_SIZE, OUTPUT_SIZE), (0, 0, 0, 0))
    canvas.alpha_composite(fitted, (D6_MARGIN, D6_MARGIN))
    return canvas


def extract_green_glyph(source: Path) -> Image.Image:
    """Extract a green D10 numeral, including its dark bevel and shadow."""
    with Image.open(source) as source_image:
        rgba = source_image.convert("RGBA")

    pixels = np.asarray(rgba)
    red = pixels[:, :, 0].astype(np.int16)
    green = pixels[:, :, 1].astype(np.int16)
    blue = pixels[:, :, 2].astype(np.int16)
    source_alpha = pixels[:, :, 3]

    # The center ROI excludes the green accent slits around the D10 perimeter.
    # Express it proportionally because packaged D10 sources are now 256px.
    roi = np.zeros(red.shape, dtype=bool)
    height, width = red.shape
    roi[round(height * 0.17):round(height * 0.79), round(width * 0.21):round(width * 0.79)] = True
    green_face = (
        roi
        & (source_alpha > 16)
        & (green > 65)
        & (green > red * 1.18)
        & (green > blue * 1.08)
    )

    connected_face = np.asarray(
        Image.fromarray((green_face * 255).astype(np.uint8), mode="L").filter(ImageFilter.MaxFilter(3)),
    ) > 0
    green_face = largest_component(connected_face)

    ys, xs = np.nonzero(green_face)
    if len(xs) < 100:
        raise ValueError(f"Could not isolate the numeral in {source}")

    margin = max(4, round(min(rgba.size) * 26 / 850))
    left = max(0, int(xs.min()) - margin)
    top = max(0, int(ys.min()) - margin)
    right = min(rgba.width, int(xs.max()) + margin + 1)
    bottom = min(rgba.height, int(ys.max()) + margin + 1)

    colored_mask = Image.fromarray((green_face * 255).astype(np.uint8), mode="L")
    # Expand around the colored face to retain the numeral's black outline and
    # beveled shadow, then lightly feather the cutout.
    dilation = max(3, round(min(rgba.size) * 31 / 850))
    if dilation % 2 == 0:
        dilation += 1
    glyph_mask = colored_mask.filter(ImageFilter.MaxFilter(dilation)).filter(ImageFilter.GaussianBlur(0.8))
    glyph_mask = Image.fromarray(
        np.minimum(np.asarray(glyph_mask), source_alpha).astype(np.uint8),
        mode="L",
    )
    rgba.putalpha(glyph_mask)
    return rgba.crop((left, top, right, bottom))


def fit_glyph(glyph: Image.Image) -> Image.Image:
    width_limit = 360
    height_limit = 385
    scale = min(width_limit / glyph.width, height_limit / glyph.height)
    size = (max(1, round(glyph.width * scale)), max(1, round(glyph.height * scale)))
    return glyph.resize(size, Image.Resampling.LANCZOS)


def build_purple_set(base_source: Path, dice_root: Path) -> None:
    base = clean_die(base_source)
    destination = dice_root / "purple-green"
    destination.mkdir(parents=True, exist_ok=True)

    for face in range(1, 7):
        glyph_source = destination / f"d10_{face}.webp"
        glyph = fit_glyph(extract_green_glyph(glyph_source))
        output = base.copy()
        x = (COMPOSE_SIZE - glyph.width) // 2
        y = 438 - glyph.height // 2
        output.alpha_composite(glyph, (x, y))
        save_webp(normalize_d6_canvas(output), destination / f"d6_{face}.webp")


def build_red_preem(source: Path, dice_root: Path) -> None:
    output = clean_die(source)
    destination = dice_root / "red-blue"
    destination.mkdir(parents=True, exist_ok=True)
    save_webp(normalize_d6_canvas(output), destination / "d6_6_preem.webp")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--purple-base", type=Path, required=True)
    parser.add_argument("--red-preem", type=Path, required=True)
    parser.add_argument("--dice-root", type=Path, required=True)
    args = parser.parse_args()

    build_purple_set(args.purple_base, args.dice_root)
    build_red_preem(args.red_preem, args.dice_root)


if __name__ == "__main__":
    main()
