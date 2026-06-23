import Phaser from "phaser";
import { Hud } from "../ui/Hud";
export class UIScene extends Phaser.Scene {
  constructor() {
    super("UI");
  }
  create(): void {
    new Hud(this);
  }
}
