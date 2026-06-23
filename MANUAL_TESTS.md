# Crash Courier Manual Test Checklist

1. Run `npm run dev` and open the local URL in desktop Chrome.
2. Confirm title appears, then press Space or tap to enter gameplay in under 3 seconds.
3. Drive with WASD/arrows, pick up the highlighted parcel, and deliver it to the green zone.
4. Confirm HUD updates score, cash, combo, run timer, delivery timer, van health, and parcel integrity.
5. Brush past traffic to trigger a near-miss toast; crash into traffic/walls to confirm damage flash and camera shake.
6. Press `R` during a run and confirm the results screen appears, then restart without page reload.
7. Refresh after earning cash and confirm title screen bank/best score persists.
8. Use a mobile viewport or device in landscape and confirm on-screen steer/brake controls work.
9. Confirm no errors occur when `window.CrazyGames` is absent.
10. Run `npm run build` and verify the production build completes.
