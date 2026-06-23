import Phaser from "phaser";
import { TrafficCar } from "../entities/TrafficCar";
export class TrafficSystem {
  cars: TrafficCar[] = [];
  constructor(scene: Phaser.Scene, count: number, speed: number) {
    const routes = [
      [
        new Phaser.Math.Vector2(190, 170),
        new Phaser.Math.Vector2(1080, 170),
        new Phaser.Math.Vector2(1080, 540),
        new Phaser.Math.Vector2(190, 540),
      ],
      [new Phaser.Math.Vector2(640, 110), new Phaser.Math.Vector2(640, 610)],
      [new Phaser.Math.Vector2(1080, 320), new Phaser.Math.Vector2(180, 320)],
    ];
    for (let i = 0; i < count; i++) {
      const r = routes[i % routes.length];
      const p = r[i % r.length];
      this.cars.push(
        new TrafficCar(scene, p.x + i * 18, p.y, r, speed + 0.12 * (i % 3)),
      );
    }
  }
  update(): void {
    for (const c of this.cars) c.update();
  }
}
