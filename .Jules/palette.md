## 2026-08-31 - Alert Close Buttons Focus & ARIA
**Learning:** Dismissable alert buttons in Jinja2 templates were missing explicit `type="button"` and `aria-label`, leaving screen-reader users with unlabelled controls and potential unwanted form submissions.
**Action:** Always specify `type="button"`, `aria-label`, and clear `:focus-visible` styling for close/icon buttons across templates.
