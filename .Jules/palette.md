## 2026-09-15 - Alert Close Button Accessibility & Focus Indicators

**Learning:** Icon-only close buttons (such as `✕`) on alert containers need explicit `aria-label` attributes for screen readers to convey purpose, alongside `role="alert"` on the alert parent. Additionally, borderless icon buttons must explicitly specify `:focus-visible` styles so keyboard navigators have clear visual focus indicators.
**Action:** Always verify icon-only buttons have accessible names (`aria-label`) and distinct `:focus-visible` outlines when styling custom UI buttons.
