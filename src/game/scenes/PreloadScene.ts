import Phaser from "phaser";
export class PreloadScene extends Phaser.Scene {
  constructor() {
    super("Preload");
  }
  create(): void {
    const g = this.add.graphics();
    g.fillStyle(0x38bdf8)
      .fillRoundedRect(0, 0, 54, 92, 10)
      .lineStyle(4, 0x0f172a)
      .strokeRoundedRect(0, 0, 54, 92, 10);
    g.generateTexture("van", 54, 92);
    g.clear()
      .fillStyle(0xf97316)
      .fillRoundedRect(0, 0, 48, 82, 8)
      .lineStyle(3, 0x111827)
      .strokeRoundedRect(0, 0, 48, 82, 8);
    g.generateTexture("traffic", 48, 82);
    g.destroy();
    this.scene.start("Title");
  }
}
