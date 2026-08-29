const MODULE_ID = "pneuma-chat-dice";
const SYSTEM_DICE_ROOT = "systems/cyberpunk-red-core/icons/dice/";
const MODULE_DICE_ROOT = `modules/${MODULE_ID}/icons/dice/`;
const SYSTEM_DIE_PATTERN = /^(black|red)\/(d10|d6)_(\d+)(?:_(preem|fail))?\.svg(?:[?#].*)?$/i;

function systemDie(source) {
  if (!source) return null;

  const markerIndex = source.indexOf(SYSTEM_DICE_ROOT);
  if (markerIndex === -1) return null;

  const systemPath = source.slice(markerIndex + SYSTEM_DICE_ROOT.length);
  const match = systemPath.match(SYSTEM_DIE_PATTERN);
  if (!match) return null;

  const [, stockColor, die, faceText, special] = match;
  return { stockColor, die, face: Number(faceText), special };
}

function replacementPath(source) {
  const dieData = systemDie(source);
  if (!dieData) return null;

  const { stockColor, die, face, special } = dieData;

  if (die === "d10" && face >= 1 && face <= 10) {
    const theme = stockColor === "black" ? "purple-green" : "red-blue";
    const replacementFace = special === "preem" ? "flame" : special === "fail" ? "skull" : face;
    return `${MODULE_DICE_ROOT}${theme}/d10_${replacementFace}.webp`;
  }

  if (die === "d6" && face >= 1 && face <= 6) {
    if (stockColor === "red" && special === "preem" && face === 6) {
      return `${MODULE_DICE_ROOT}red-blue/d6_6_preem.webp`;
    }
    if (stockColor === "black" && !special) {
      return `${MODULE_DICE_ROOT}purple-green/d6_${face}.webp`;
    }
  }

  return null;
}

function replaceImage(image, originalSource, replacementSource) {
  if (!replacementSource || replacementSource === originalSource) return;

  image.addEventListener(
    "error",
    () => image.setAttribute("src", originalSource),
    { once: true },
  );
  image.setAttribute("src", replacementSource);
}

function replaceDamageDice(diceContainer) {
  const dice = [...diceContainer.querySelectorAll("img[src]")]
    .map((image) => {
      const originalSource = image.getAttribute("src");
      return { image, originalSource, dieData: systemDie(originalSource) };
    })
    .filter(({ dieData }) => dieData?.die === "d6" && dieData.face >= 1 && dieData.face <= 6);

  const sixCount = dice.filter(({ dieData }) => dieData.face === 6).length;

  for (const { image, originalSource, dieData } of dice) {
    const isPreem = dieData.face === 6 && sixCount >= 2;
    const replacementSource = isPreem
      ? `${MODULE_DICE_ROOT}red-blue/d6_6_preem.webp`
      : `${MODULE_DICE_ROOT}purple-green/d6_${dieData.face}.webp`;
    replaceImage(image, originalSource, replacementSource);
  }

  return dice.map(({ image }) => image);
}

function replaceChatDice(html) {
  const root = html?.querySelectorAll ? html : html?.[0];
  if (!root?.querySelectorAll) return;

  const damageDice = new Set();
  for (const diceContainer of root.querySelectorAll(".d6-dice-div")) {
    for (const image of replaceDamageDice(diceContainer)) damageDice.add(image);
  }

  for (const image of root.querySelectorAll("img[src]")) {
    if (damageDice.has(image)) continue;

    const originalSource = image.getAttribute("src");
    const replacementSource = originalSource && replacementPath(originalSource);
    replaceImage(image, originalSource, replacementSource);
  }
}

Hooks.once("init", () => {
  console.info(`${MODULE_ID} | Initializing`);
});

Hooks.on("renderChatMessage", (_message, html) => {
  replaceChatDice(html);
});
