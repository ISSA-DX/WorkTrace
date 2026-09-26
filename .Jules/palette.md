# Palette's Journal - UX & Accessibility Learnings

## 2025-05-18 - Flash Notification Dismiss Buttons
**Learning:** Flash message close buttons rendered with raw unicode characters like `✕` without `aria-label` or explicit `type="button"` are announced confusingly by screen readers (e.g. "multiplication sign button") and lack clear keyboard focus styles (`:focus-visible`).
**Action:** Always include `type="button"`, `aria-label="Dismiss alert"`, and explicit `:focus-visible` ring/outline styles for icon-only alert dismiss buttons in templates.
