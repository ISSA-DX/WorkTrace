## 2025-05-24 - Flash Alert Dismiss Button Accessibility
**Learning:** Flash message close buttons using unicode characters like '✕' lack semantic labels for screen readers and default focus styling for keyboard navigation. Adding `role="alert"` on alert containers ensures screen readers announce flashed alerts immediately upon page load.
**Action:** Always include `role="alert"` on banner messages, explicit `type="button"`, `aria-label="Dismiss notification"`, and visible `:focus-visible` ring outlines on close icons.
