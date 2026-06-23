import Phaser from "phaser";
import tuning from "./tuning.json";
import { BootScene } from "../scenes/BootScene";
import { PreloadScene } from "../scenes/PreloadScene";
import { TitleScene } from "../scenes/TitleScene";
import { RunScene } from "../scenes/RunScene";
import { UIScene } from "../scenes/UIScene";
import { ResultsScene } from "../scenes/ResultsScene";

export const TUNING = tuning;
export const GAME_WIDTH = 1280;
export const GAME_HEIGHT = 720;

export function buildGameConfig(parent: string): Phaser.Types.Core.GameConfig {
  return {
    type: Phaser.AUTO,
    parent,
    width: GAME_WIDTH,
    height: GAME_HEIGHT,
    backgroundColor: "#16202b",
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    physics: {
      default: "matter",
      matter: { gravity: { x: 0, y: 0 }, debug: false, enableSleeping: false },
    },
    scene: [
      BootScene,
      PreloadScene,
      TitleScene,
      RunScene,
      UIScene,
      ResultsScene,
    ],
  };
}
