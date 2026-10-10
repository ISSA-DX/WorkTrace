## 2026-10-10 - Accessible Flash Alert Close Buttons
**Learning:** Flash notification alerts in Jinja templates used symbol-only buttons (`✕`) without `type="button"` or `aria-label="Close alert"`, preventing screen readers from identifying the button purpose and risking unexpected form submission when placed near forms.
**Action:** Always include `type="button"`, `aria-label="Close alert"`, and `:focus-visible` styling on icon/symbol dismiss buttons.
