## 2026-10-30 - Accessible Alert Dismiss Buttons and Keyboard Navigation Indicators
**Learning:** Flash message close buttons using icon glyphs (e.g., ✕) lack accessible names for screen readers and missing explicit `type="button"` attributes can cause unintended form behavior. Additionally, custom styled interactive controls require explicit `:focus-visible` ring/outline styles for keyboard accessibility.
**Action:** Always ensure icon-only buttons include `type="button"` and `aria-label`, and verify standard `:focus-visible` outlines exist on all interactive HTML elements.
