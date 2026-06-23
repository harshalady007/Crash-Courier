import Phaser from 'phaser';
export class UpgradePanel { static toast(scene:Phaser.Scene,msg:string):void{ const t=scene.add.text(640,96,msg,{fontSize:'24px',color:'#fef3c7',backgroundColor:'#111827cc',padding:{x:12,y:8}}).setOrigin(0.5).setScrollFactor(0).setDepth(250); scene.tweens.add({targets:t,alpha:0,y:70,duration:1400,onComplete:()=>t.destroy()}); } }
