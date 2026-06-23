import Phaser from "phaser";
export class DeliveryZone {
  marker: Phaser.GameObjects.Arc;
  label: Phaser.GameObjects.Text;
  constructor(
    scene: Phaser.Scene,
    x: number,
    y: number,
    color: number,
    text: string,
  ) {
    this.marker = scene.add
      .circle(x, y, 36, color, 0.35)
      .setStrokeStyle(4, color);
    this.label = scene.add
      .text(x, y - 62, text, {
        fontSize: "20px",
        color: "#ffffff",
        stroke: "#111827",
        strokeThickness: 4,
      })
      .setOrigin(0.5);
  }
  set(x: number, y: number, text: string, color: number): void {
    this.marker
      .setPosition(x, y)
      .setFillStyle(color, 0.35)
      .setStrokeStyle(4, color);
    this.label.setPosition(x, y - 62).setText(text);
  }
  destroy(): void {
    this.marker.destroy();
    this.label.destroy();
  }
}
