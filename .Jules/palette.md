## 2026-11-04 - Accessible Alert Dismissal and Keyboard Focus Indicators
**Learning:** Flash alerts and icon-only dismiss buttons across templates lacked accessible names (`aria-label`) and alert live region semantics (`role="alert"`), leaving screen-reader users uninformed and keyboard navigators without distinct focus outlines on buttons and alert actions.
**Action:** Always provide `role="alert"` and explicit `aria-label="Dismiss alert"` on alert close buttons, complemented by high-contrast `:focus-visible` ring styling on buttons and interactive controls using existing palette tokens.
