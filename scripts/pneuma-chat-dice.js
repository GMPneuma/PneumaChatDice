const MODULE_ID = "pneuma-chat-dice";
const SYSTEM_DICE_ROOT = "systems/cyberpunk-red-core/icons/dice/";
const MODULE_DICE_ROOT = `modules/${MODULE_ID}/icons/dice/`;
const SYSTEM_DIE_PATTERN = /^(black|red)\/(d10|d6)_(\d+)(?:_(preem|fail))?\.svg(?:[?#].*)?$/i;

function replacementPath(source) {
  const markerIndex = source.indexOf(SYSTEM_DICE_ROOT);
  if (markerIndex === -1) return null;

  const systemPath = source.slice(markerIndex + SYSTEM_DICE_ROOT.length);
  const match = systemPath.match(SYSTEM_DIE_PATTERN);
  if (!match) return null;

  const [, stockColor, die, faceText, special] = match;
  const face = Number(faceText);

  if (die === "d10" && face >= 1 && face <= 10) {
    const theme = stockColor === "black" ? "purple-green" : "red-blue";
    const replacementFace = special === "preem" ? "flame" : special === "fail" ? "skull" : face;
    return `${MODULE_DICE_ROOT}${theme}/d10_${replacementFace}.png`;
  }

  if (die === "d6" && face >= 1 && face <= 6) {
    if (stockColor === "red" && special === "preem" && face === 6) {
      return `${MODULE_DICE_ROOT}red-blue/d6_6_preem.png`;
    }
    if (stockColor === "black" && !special) {
      return `${MODULE_DICE_ROOT}purple-green/d6_${face}.png`;
    }
  }

  return null;
}

function replaceChatDice(html) {
  const root = html?.querySelectorAll ? html : html?.[0];
  if (!root?.querySelectorAll) return;

  for (const image of root.querySelectorAll("img[src]")) {
    const originalSource = image.getAttribute("src");
    const replacementSource = originalSource && replacementPath(originalSource);
    if (!replacementSource) continue;

    image.addEventListener(
      "error",
      () => image.setAttribute("src", originalSource),
      { once: true },
    );
    image.setAttribute("src", replacementSource);
  }
}

Hooks.once("init", () => {
  console.info(`${MODULE_ID} | Initializing`);
});

Hooks.on("renderChatMessage", (_message, html) => {
  replaceChatDice(html);
});
