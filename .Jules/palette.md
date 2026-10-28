## 2026-10-28 - Icon-only Alert Dismiss Buttons A11y Pattern
**Learning:** Icon-only close buttons (`✕`) on flash alerts need explicit `aria-label="Dismiss alert"` and `type="button"` to support screen readers and prevent accidental form submission when rendered inside forms, along with `:focus-visible` ring/outline for keyboard navigation.
**Action:** Always add `type="button"`, `aria-label`, and `:focus-visible` styling when implementing dismissible alert components.
