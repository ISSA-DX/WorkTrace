## 2025-03-30 - Accessible Flash Alert Close Buttons
**Learning:** Non-standard icon-only dismiss buttons (like `✕` on alerts) without `type="button"` or an `aria-label` are unannounced or read as raw characters by screen readers and can behave unexpectedly inside form contexts if `type` defaults to `submit`.
**Action:** Always provide `type="button"` and `aria-label="Close notification"` (or similar explicit accessible name) for close/dismiss icon buttons in template alerts and modals.
