# Palette's UX Journal

## 2026-05-24 - Accessible Copy-to-Clipboard Interactions
**Learning:** Copy buttons that only update visually (e.g. changing text or showing a checkmark) leave screen reader users unaware of the action's success. Standard copy operations should provide a screen-reader announcement (via `aria-live` or temporary status elements) to confirm the copy succeeded.
**Action:** Use `aria-live="polite"` on a dynamic status container or update the button's `aria-label`/text with clear auditory feedback ("URL copied to clipboard") to ensure accessibility.
