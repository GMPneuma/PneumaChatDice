# Pneuma Chat Dice

Pneuma Chat Dice is a Foundry Virtual Tabletop module for **Cyberpunk RED - CORE**. It changes only the dice artwork displayed in chat cards; roll mechanics and results remain untouched.

## Installation

Paste this manifest URL into Foundry VTT's **Install Module** dialog:

```text
https://github.com/GMPneuma/PneumaChatDice/releases/latest/download/module.json
```

After installation, enable **Pneuma Chat Dice** in the Cyberpunk RED world.

Releases and manual ZIP downloads are available from:

```text
https://github.com/GMPneuma/PneumaChatDice/releases
```

## Dice mapping

| Cyberpunk RED chat die | Pneuma replacement |
| --- | --- |
| Standard D10, faces 1-10 | Purple with green accents |
| Critical follow-up D10, faces 1-10 | Red with blue accents |
| Critical success D10 | Red/blue flame |
| Critical failure D10 | Red/blue skull |
| Standard D6, faces 1-6 | Purple with green accents |
| Critical-success D6 showing 6 | Red/blue PREEM 6 |

## Compatibility

Version 0.1.1 targets:

- Foundry Virtual Tabletop 11-12
- Cyberpunk RED - CORE v0.88.2

The module uses the system's existing chat-card classes and replaces image paths only after a chat message renders.

## Asset layout

- `icons/dice/purple-green/` contains the standard D10 PNGs and D6 SVGs.
- `icons/dice/red-blue/` contains the critical D10 PNGs and special PREEM D6 SVG.

The D10 artwork is stored directly as transparent 850×850 PNGs. The D6 artwork is compact native SVG so it stays crisp at chat size.

The asset builders are retained in `scripts/build_dice_svgs.py` and `scripts/build_d6_svgs.py` for reproducible development builds.

## License

No license has been selected. All rights are reserved.
