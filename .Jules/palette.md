## 2025-05-24 - Alert Close Buttons ARIA & Focus States
**Learning:** Icon-only close buttons (like `✕` in flash alert banners) lack accessible names for screen readers and missing explicit `:focus-visible` styles for keyboard navigation.
**Action:** Always provide `aria-label="Dismiss alert"`, `type="button"`, and `:focus-visible` outline/ring styles using existing design tokens for icon-only alert close controls.
