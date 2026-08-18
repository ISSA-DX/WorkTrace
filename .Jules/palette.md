## 2025-05-18 - Accessible Alert Dismiss Buttons
**Learning:** Icon-only close buttons (like '✕' in alert/flash messages) are unannounced or poorly announced by screen readers without explicit ARIA labels.
**Action:** Always include `aria-label="Close message"` (or contextual label) on modal and alert close buttons across templates.
