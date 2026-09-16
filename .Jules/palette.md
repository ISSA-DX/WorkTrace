# Palette's UX & Accessibility Journal

## 2026-09-16 - Alert Dismiss Button Accessibility
**Learning:** Dismiss buttons in flash messages using pure unicode symbols (`✕`) without `type="button"` and `aria-label` are unannounced or poorly announced by screen readers and default to submit buttons inside forms if placed inside form tags. Additionally, borderless icon buttons need distinct `:focus-visible` styling for keyboard navigation.
**Action:** Always include `type="button"`, `aria-label="Dismiss alert"`, and custom `:focus-visible` outline styles for dismissible message UI components across templates.
