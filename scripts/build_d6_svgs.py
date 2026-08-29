"""Build restrained D6 variants by recoloring Cyberpunk RED's native SVG art."""

from __future__ import annotations

import argparse
from pathlib import Path


PURPLE_GREEN = {
    "#242322": "#160d1f",
    "#595652": "#351044",
    "#696a6a": "#531567",
    "#847e87": "#8a2aa0",
    "#9badb7": "#39ff6a",
    "#f4f4f4": "#b8ffc7",
}

RED_BLUE_PREEM = {
    "#663931": "#3a1018",
    "#8f563b": "#681724",
    "#ac3232": "#a60820",
    "#d95763": "#e33348",
    "#df7126": "#168fc4",
    "#fbf236": "#36ddff",
    "#9badb7": "#8cecff",
    "#f4f4f4": "#e9fbff",
}


def recolor(source: Path, destination: Path, palette: dict[str, str]) -> None:
    svg = source.read_text(encoding="utf-8")
    for original, replacement in palette.items():
        svg = svg.replace(original, replacement)
        svg = svg.replace(original.upper(), replacement)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock-dice-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    for face in range(1, 7):
        recolor(
            args.stock_dice_root / "black" / f"d6_{face}.svg",
            args.output_root / "purple-green" / f"d6_{face}.svg",
            PURPLE_GREEN,
        )

    recolor(
        args.stock_dice_root / "red" / "d6_6_preem.svg",
        args.output_root / "red-blue" / "d6_6_preem.svg",
        RED_BLUE_PREEM,
    )


if __name__ == "__main__":
    main()
