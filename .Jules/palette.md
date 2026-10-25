## 2025-05-24 - Flash Alert Dismiss Button Accessibility
**Learning:** Icon-only close buttons (`✕`) in alert banners need explicit `aria-label` attributes (e.g. `aria-label="Close notification"`) and `:focus-visible` outline styles so screen reader users and keyboard users can easily identify and interact with them.
**Action:** Always add `aria-label` and `:focus-visible` styling when using icon-only close buttons in notification banners.
