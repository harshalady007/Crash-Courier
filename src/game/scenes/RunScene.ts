import Phaser from "phaser";
import { TUNING } from "../config/gameConfig";
import { PARCEL_TYPES, type ParcelTypeId } from "../data/balanceConfig";
import { PlayerVan } from "../entities/PlayerVan";
import { Parcel } from "../entities/Parcel";
import { DeliveryZone } from "../entities/DeliveryZone";
import { calculateDeliveryReward } from "../systems/DeliverySystem";
import { InputSystem } from "../systems/InputSystem";
import { SaveSystem } from "../systems/SaveSystem";
import { modifiersFor } from "../systems/UpgradeSystem";
import { TrafficSystem } from "../systems/TrafficSystem";
import { EffectsSystem } from "../systems/EffectsSystem";
import { TouchControls } from "../ui/TouchControls";
import { UpgradePanel } from "../ui/UpgradePanel";
import { EVENTS } from "../utils/events";
import { distance, randomItem } from "../utils/math";
import type { CrazyGamesBridge } from "../sdk/CrazyGamesBridge";
const POINTS = [
  { x: 190, y: 170 },
  { x: 640, y: 170 },
  { x: 1080, y: 170 },
  { x: 190, y: 320 },
  { x: 640, y: 320 },
  { x: 1080, y: 320 },
  { x: 190, y: 540 },
  { x: 640, y: 540 },
  { x: 1080, y: 540 },
];
export class RunScene extends Phaser.Scene {
  private inputSystem!: InputSystem;
  private player!: PlayerVan;
  private traffic!: TrafficSystem;
  private effects!: EffectsSystem;
  private save = new SaveSystem();
  private parcel!: Parcel;
  private pickup!: DeliveryZone;
  private dropoff!: DeliveryZone;
  private hasParcel = false;
  private runTime = TUNING.run.startSeconds;
  private deliveryTime = TUNING.delivery.baseSeconds;
  private elapsedDelivery = 0;
  private score = 0;
  private cash = 0;
  private combo = 1;
  private deliveries = 0;
  private nearMisses = 0;
  private nearMissCooldown = 0;
  private profile = this.save.load();
  private mods = modifiersFor(this.profile);
  constructor() {
    super("Run");
  }
  create(): void {
    this.profile = this.save.load();
    this.mods = modifiersFor(this.profile);
    this.runTime = TUNING.run.startSeconds;
    this.score = 0;
    this.cash = 0;
    this.combo = 1;
    this.deliveries = 0;
    this.nearMisses = 0;
    this.hasParcel = false;
    this.matter.world.setBounds(0, 0, 1280, 720, 48);
    this.drawMap();
    this.inputSystem = new InputSystem(this);
    new TouchControls(this, this.inputSystem);
    this.effects = new EffectsSystem(this);
    this.player = new PlayerVan(
      this,
      640,
      620,
      TUNING.run.maxHealth + this.mods.maxHealthBonus,
      this.mods.maxSpeedMultiplier,
      this.mods.turnMultiplier,
    );
    this.traffic = new TrafficSystem(
      this,
      TUNING.traffic.count,
      TUNING.traffic.speed,
    );
    this.pickup = new DeliveryZone(this, 0, 0, 0xfacc15, "PICKUP");
    this.dropoff = new DeliveryZone(this, 0, 0, 0x22c55e, "DROP");
    this.dropoff.marker.setVisible(false);
    this.dropoff.label.setVisible(false);
    this.spawnDelivery();
    this.matter.world.on(
      "collisionstart",
      (e: Phaser.Physics.Matter.Events.CollisionStartEvent) =>
        this.onCollision(e),
    );
    (this.registry.get("cg") as CrazyGamesBridge | undefined)?.gameplayStart();
  }
  update(_t: number, deltaMs: number): void {
    const dt = Math.min(deltaMs / 1000, 0.05);
    if (this.inputSystem.restartPressed) return this.finish("Restarted");
    if (this.inputSystem.pausePressed) {
      this.scene.pause();
      this.scene.launch("Results", {
        score: this.score,
        cash: this.cash,
        deliveries: this.deliveries,
        reason: "Paused",
        profile: this.profile,
      });
      return;
    }
    this.player.update(this.inputSystem.controls(TUNING.mobile.autoThrottle));
    this.traffic.update();
    this.runTime -= dt;
    this.deliveryTime -= dt;
    this.elapsedDelivery += dt;
    this.nearMissCooldown = Math.max(0, this.nearMissCooldown - dt);
    this.checkZones();
    this.checkNearMiss();
    this.emitHud();
    if (this.runTime <= 0 || this.deliveryTime <= 0)
      this.finish("Timer expired");
    if (this.player.health <= 0) this.finish("Van destroyed");
    if (this.parcel.integrity <= 0) this.finish("Parcel ruined");
  }
  private drawMap(): void {
    this.add.rectangle(640, 360, 1280, 720, 0x14532d);
    const roads = [
      [640, 170, 1080, 92],
      [640, 320, 1080, 92],
      [640, 540, 1080, 92],
      [190, 355, 92, 460],
      [640, 355, 92, 460],
      [1080, 355, 92, 460],
    ];
    for (const r of roads) this.add.rectangle(r[0], r[1], r[2], r[3], 0x374151);
    for (let x = 320; x <= 960; x += 320)
      for (let y = 245; y <= 455; y += 210)
        this.add.rectangle(x, y, 150, 96, 0x1f2937).setStrokeStyle(3, 0x4b5563);
    this.add
      .text(24, 680, "WASD/Arrows drive • R restart • P pause", {
        fontSize: "18px",
        color: "#cbd5e1",
      })
      .setScrollFactor(0);
  }
  private spawnDelivery(): void {
    const type = randomItem(Object.keys(PARCEL_TYPES) as ParcelTypeId[]);
    this.parcel = new Parcel(type, TUNING.run.maxParcelIntegrity);
    const a = randomItem(POINTS),
      b = randomItem(POINTS.filter((p) => distance(p, a) > 360));
    this.pickup.set(a.x, a.y, `PICKUP ${PARCEL_TYPES[type].label}`, 0xfacc15);
    this.dropoff.set(b.x, b.y, "DROP OFF", 0x22c55e);
    this.dropoff.marker.setVisible(false);
    this.dropoff.label.setVisible(false);
    this.hasParcel = false;
    this.deliveryTime = Phaser.Math.Clamp(
      TUNING.delivery.baseSeconds - this.deliveries * 0.8,
      TUNING.delivery.minSeconds,
      40,
    );
    this.elapsedDelivery = 0;
    this.nearMisses = 0;
  }
  private checkZones(): void {
    const pos = { x: this.player.sprite.x, y: this.player.sprite.y };
    if (
      !this.hasParcel &&
      distance(pos, this.pickup.marker) < TUNING.delivery.pickupRadius
    ) {
      this.hasParcel = true;
      this.pickup.marker.setVisible(false);
      this.pickup.label.setVisible(false);
      this.dropoff.marker.setVisible(true);
      this.dropoff.label.setVisible(true);
      this.effects.burst(pos.x, pos.y);
    }
    if (
      this.hasParcel &&
      distance(pos, this.dropoff.marker) < TUNING.delivery.dropoffRadius
    ) {
      const reward = calculateDeliveryReward({
        baseCash: TUNING.delivery.baseCash,
        elapsedSeconds: this.elapsedDelivery,
        targetSeconds: TUNING.delivery.baseSeconds,
        nearMisses: this.nearMisses,
        combo: this.combo,
        parcelType: this.parcel.type,
        cashMultiplier: this.mods.cashMultiplier,
      });
      this.cash += reward.cash;
      this.score += reward.score;
      this.profile.cash += reward.cash;
      this.combo++;
      this.deliveries++;
      this.runTime += TUNING.delivery.timeExtension;
      this.save.save(this.profile);
      this.effects.burst(pos.x, pos.y);
      UpgradePanel.toast(
        this,
        `Delivered! +$${reward.cash}  +${TUNING.delivery.timeExtension}s`,
      );
      if (this.deliveries % 3 === 0)
        UpgradePanel.toast(
          this,
          "Upgrade choices unlock after this prototype run.",
        );
      this.spawnDelivery();
    }
  }
  private checkNearMiss(): void {
    if (this.nearMissCooldown > 0) return;
    for (const car of this.traffic.cars) {
      const d = distance(this.player.sprite, car.sprite);
      if (
        d < TUNING.traffic.nearMissDistance &&
        d > 48 &&
        this.player.speed > 3
      ) {
        this.nearMisses++;
        this.score += 25 * this.combo;
        this.nearMissCooldown = 0.55;
        UpgradePanel.toast(this, "Near miss!");
        break;
      }
    }
  }
  private onCollision(
    e: Phaser.Physics.Matter.Events.CollisionStartEvent,
  ): void {
    for (const pair of e.pairs) {
      const impact = Math.abs(pair.collision.depth) * (this.player.speed + 1);
      if (impact > 1.4) {
        const parcelDef = PARCEL_TYPES[this.parcel.type];
        this.player.damage(impact * TUNING.player.crashDamageScale);
        this.parcel.damage(
          impact *
            TUNING.player.parcelDamageScale *
            parcelDef.damageMultiplier *
            this.mods.parcelDamageMultiplier,
        );
        this.effects.hit(
          this.player.sprite.x,
          this.player.sprite.y,
          impact > 3,
        );
      }
    }
  }
  private emitHud(): void {
    this.game.events.emit(EVENTS.hud, {
      score: this.score,
      cash: this.cash,
      combo: this.combo,
      time: this.runTime,
      deliveryTime: this.deliveryTime,
      health: this.player.health,
      parcel: this.parcel.integrity,
      objective: this.hasParcel ? "Deliver the parcel!" : "Grab the pickup!",
    });
  }
  private finish(reason: string): void {
    (this.registry.get("cg") as CrazyGamesBridge | undefined)?.gameplayStop();
    this.profile.bestScore = Math.max(this.profile.bestScore, this.score);
    this.save.save(this.profile);
    this.scene.stop("UI");
    this.scene.start("Results", {
      score: this.score,
      cash: this.cash,
      deliveries: this.deliveries,
      reason,
      profile: this.profile,
    });
  }
}
