## 2025-05-24 - Flash Message Close Button Accessibility
**Learning:** Alert dismiss buttons in base templates are icon-only (`✕`) and easily missed by screen readers and keyboard navigation unless explicitly given `aria-label` and `:focus-visible` styles.
**Action:** Always verify `aria-label="Dismiss alert"` and visible focus ring indicators on dismiss/close buttons across all base layout templates.
