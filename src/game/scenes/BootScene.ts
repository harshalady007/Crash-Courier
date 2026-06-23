import Phaser from 'phaser';
import { CrazyGamesBridge } from '../sdk/CrazyGamesBridge';
export class BootScene extends Phaser.Scene { constructor(){ super('Boot'); } async create(): Promise<void>{ const bridge=new CrazyGamesBridge(); this.registry.set('cg',bridge); bridge.loadingStart(); await bridge.init(); bridge.loadingStop(); this.scene.start('Preload'); } }
