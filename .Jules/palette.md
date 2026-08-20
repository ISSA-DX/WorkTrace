## 2026-08-20 - Flash Alert Close Buttons Accessibility & Focus Styles
**Learning:** Flash alert dismiss buttons (`✕`) were missing `aria-label` and `type="button"`, causing screen readers to misidentify them or treat them as form submit buttons when inside forms. Adding `:focus-visible` ring styles on interactive elements provides clear keyboard navigation without affecting mouse clicks.
**Action:** Always verify icon-only buttons have explicit `aria-label` and `type="button"` attributes, and maintain global `:focus-visible` outline styles.
