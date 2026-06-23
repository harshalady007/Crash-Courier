import Phaser from "phaser";
import type { Profile } from "../data/defaultProfile";
export type ResultsData = {
  score: number;
  cash: number;
  deliveries: number;
  reason: string;
  profile: Profile;
};
export class ResultsScene extends Phaser.Scene {
  constructor() {
    super("Results");
  }
  create(data: ResultsData): void {
    this.add.rectangle(640, 360, 1280, 720, 0x111827, 0.96);
    this.add
      .text(640, 170, "RUN COMPLETE", {
        fontSize: "58px",
        color: "#f87171",
        stroke: "#000",
        strokeThickness: 6,
      })
      .setOrigin(0.5);
    this.add
      .text(
        640,
        290,
        `Reason: ${data.reason}\nDeliveries: ${data.deliveries}\nScore: ${data.score}\nRun Cash: $${data.cash}\nBank: $${data.profile.cash}\nBest: ${data.profile.bestScore}`,
        { fontSize: "28px", color: "#fff", align: "center" },
      )
      .setOrigin(0.5);
    this.add
      .text(640, 540, "Press R / Space or Tap to Restart", {
        fontSize: "30px",
        color: "#facc15",
      })
      .setOrigin(0.5);
    const restart = () => {
      this.scene.stop("UI");
      this.scene.start("Run");
      this.scene.launch("UI");
    };
    this.input.once("pointerdown", restart);
    this.input.keyboard?.once("keydown-R", restart);
    this.input.keyboard?.once("keydown-SPACE", restart);
  }
}
