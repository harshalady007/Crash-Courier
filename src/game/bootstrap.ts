import Phaser from 'phaser';
import { buildGameConfig } from './config/gameConfig';

export function createGame(parent: string): Phaser.Game {
  return new Phaser.Game(buildGameConfig(parent));
}
