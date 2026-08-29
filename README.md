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
| Critical failure D10 | Color-matched cracked skull |
| Damage D6, including a lone 6 | Purple with green accents |
| Damage roll containing 2+ sixes | Every 6 becomes the red/blue PREEM 6; all other dice stay purple |

## Compatibility

Version 0.8.2 targets:

- Foundry Virtual Tabletop 11-12
- Cyberpunk RED - CORE v0.88.2

The module uses the system's existing chat-card classes and replaces image paths only after a chat message renders.

## Asset layout

- `icons/dice/purple-green/` contains the standard D10 and D6 WebP assets.
- `icons/dice/red-blue/` contains the critical D10 WebP assets and special PREEM D6 WebP.

All shipped dice artwork is stored as transparent 256×256 WebP at quality 90. The artwork is designed and checked at the system's approximately 70-pixel chat size.

The asset builders are retained in `scripts/build_dice_svgs.py` and `scripts/build_d6_pngs.py` for reproducible development builds.

## License

No license has been selected. All rights are reserved.
