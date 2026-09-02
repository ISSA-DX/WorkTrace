# Palette's Journal - Critical Learnings

## 2025-05-24 - Flash Alert Screen Reader and Keyboard Navigation
**Learning:** Flash alerts rendered dynamically or on page load require `role="alert"` for instant screen reader announcements, and icon-only dismiss buttons (`✕`) must have explicit `aria-label="Close alert"` and `:focus-visible` focus outlines for keyboard-only users.
**Action:** Always include `role="alert"`, `aria-label`, and `:focus-visible` styles on dismissible message alerts in HTML/CSS templates.
