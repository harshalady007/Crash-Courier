import Phaser from "phaser";
import { TUNING } from "../config/gameConfig";
export type ControlState = {
  accelerate: boolean;
  brake: boolean;
  left: boolean;
  right: boolean;
};
export class PlayerVan {
  readonly sprite: Phaser.Physics.Matter.Sprite;
  health: number;
  constructor(
    private scene: Phaser.Scene,
    x: number,
    y: number,
    private maxHealth: number,
    private speedMultiplier: number,
    private turnMultiplier: number,
  ) {
    this.health = maxHealth;
    this.sprite = scene.matter.add.sprite(x, y, "van");
    this.sprite.setRectangle(54, 92);
    this.sprite.setFrictionAir(TUNING.player.drag);
    this.sprite.setMass(28);
  }
  get speed(): number {
    const v = this.sprite.body?.velocity;
    return v ? Math.hypot(v.x, v.y) : 0;
  }
  update(c: ControlState): void {
    const angle = this.sprite.rotation - Math.PI / 2;
    const speed = this.speed;
    const max = TUNING.player.maxSpeed * this.speedMultiplier;
    if (c.accelerate && speed < max)
      this.sprite.applyForce(
        new Phaser.Math.Vector2(
          Math.cos(angle) * TUNING.player.acceleration,
          Math.sin(angle) * TUNING.player.acceleration,
        ),
      );
    if (c.brake)
      this.sprite.applyForce(
        new Phaser.Math.Vector2(
          -Math.cos(angle) * TUNING.player.brake,
          -Math.sin(angle) * TUNING.player.brake,
        ),
      );
    const steer = (c.left ? -1 : 0) + (c.right ? 1 : 0);
    if (steer)
      this.sprite.setAngularVelocity(
        steer *
          TUNING.player.turnRate *
          this.turnMultiplier *
          (0.35 + Math.min(speed / max, 1)),
      );
  }
  damage(amount: number): void {
    this.health = Math.max(0, this.health - amount);
    this.sprite.setTint(0xff7777);
    this.scene.time.delayedCall(90, () => this.sprite.clearTint());
  }
  reset(x: number, y: number): void {
    this.health = this.maxHealth;
    this.sprite.setPosition(x, y);
    this.sprite.setVelocity(0, 0);
    this.sprite.setAngularVelocity(0);
    this.sprite.setRotation(0);
  }
}
