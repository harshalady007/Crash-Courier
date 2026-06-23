# Crash Courier

Crash Courier is a small Phaser 3 + TypeScript + Vite browser-game prototype for CrazyGames. The current build proves the core loop: start quickly, pick up a parcel, deliver it under pressure, dodge traffic, survive crashes, earn cash, and restart fast.

## Requirements

- Node.js 20+
- npm

## Setup

```bash
npm install
```

## How to test it

### 1. Run automated unit tests

```bash
npm run test
```

Expected result: all Vitest unit tests pass. These cover pure reward math, upgrade application, and save serialization.

### 2. Run a production build

```bash
npm run build
```

Expected result: TypeScript checking and Vite production build complete successfully. Vite may warn that the Phaser bundle chunk is larger than 500 kB; that warning is expected for this prototype and does not fail the build.

### 3. Run the local game server

```bash
npm run dev
```

Expected result: Vite prints a local URL, usually `http://localhost:5173/`.

### 4. Manual gameplay smoke test

Open the Vite URL in a desktop browser or mobile landscape viewport, then verify:

1. The title screen appears quickly.
2. Press Space/Enter or tap to start.
3. Drive with WASD or arrow keys.
4. Pick up the yellow parcel marker.
5. Deliver to the green drop-off marker.
6. Confirm score, cash, combo, timers, van health, and parcel integrity update in the HUD.
7. Brush near traffic to trigger near-miss feedback.
8. Crash into traffic or walls and confirm van/parcel damage feedback is readable.
9. Press `R` to restart through the results screen without reloading the page.
10. Refresh after earning cash and confirm saved cash/best score appears on the title screen.
11. In a mobile landscape viewport, verify the on-screen left/right/brake controls work.
12. Confirm the game runs locally without `window.CrazyGames` present.

For a shorter checklist, see [`MANUAL_TESTS.md`](./MANUAL_TESTS.md).

## Controls

| Action | Desktop | Mobile |
| --- | --- | --- |
| Accelerate | W / Up | Auto-throttle |
| Brake / reverse | S / Down | Brake button |
| Steer left | A / Left | Left button |
| Steer right | D / Right | Right button |
| Restart | R | Results tap |
| Pause | P | Not yet exposed |

## Notes for reviewers

- CrazyGames calls are guarded through `CrazyGamesBridge`, so local runs should not throw when the SDK is absent.
- Placeholder textures are generated in `PreloadScene`; no external art assets are required for the prototype.
- Gameplay tuning lives in `src/game/config/tuning.json` for quick iteration.
