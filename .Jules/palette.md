## 2025-05-24 - Accessible Alert Dismiss Buttons & Keyboard Focus States
**Learning:** Icon-only close buttons (like unicode `✕`) lack descriptive text for screen readers unless explicitly assigned an `aria-label`, leading to confusing announcements. Furthermore, custom buttons and links without `:focus-visible` styles leave keyboard-only users without a clear visual indication of active focus.
**Action:** Always provide explicit `aria-label` attributes on symbol/icon buttons and define consistent `:focus-visible` outline styles across all interactive UI controls.
