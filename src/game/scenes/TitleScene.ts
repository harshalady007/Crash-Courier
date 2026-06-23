import Phaser from "phaser";
import { SaveSystem } from "../systems/SaveSystem";
export class TitleScene extends Phaser.Scene {
  constructor() {
    super("Title");
  }
  create(): void {
    const profile = new SaveSystem().load();
    this.add.rectangle(640, 360, 1280, 720, 0x111827);
    this.add
      .text(640, 210, "CRASH COURIER", {
        fontSize: "72px",
        color: "#facc15",
        stroke: "#000",
        strokeThickness: 8,
      })
      .setOrigin(0.5);
    this.add
      .text(
        640,
        315,
        "Chain reckless deliveries. Crash funny. Keep the parcel alive.",
        { fontSize: "24px", color: "#e5e7eb" },
      )
      .setOrigin(0.5);
    this.add
      .text(
        640,
        390,
        `Best Score: ${profile.bestScore}   Bank: $${profile.cash}`,
        { fontSize: "24px", color: "#93c5fd" },
      )
      .setOrigin(0.5);
    this.add
      .text(640, 500, "Tap / Press Space / Enter to Start", {
        fontSize: "30px",
        color: "#fff",
      })
      .setOrigin(0.5);
    this.input.once("pointerdown", () => this.start());
    this.input.keyboard?.once("keydown-SPACE", () => this.start());
    this.input.keyboard?.once("keydown-ENTER", () => this.start());
  }
  private start(): void {
    this.scene.start("Run");
    this.scene.launch("UI");
  }
}
