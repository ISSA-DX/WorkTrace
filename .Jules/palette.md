## 2025-02-19 - Accessible Toggle Switches & Keyboard Focus-Visible State
**Learning:** Hiding checkbox inputs with `display: none` in toggle switches removes them completely from screen readers and tab navigation. Using visually-hidden CSS styling (`clip: rect(...)`) preserves semantic checkbox interaction and allows `:focus-visible` styling on `.toggle-slider`.
**Action:** Always visually hide checkbox inputs in custom toggles instead of `display: none` and bind `:focus-visible` outline to the visible switch container.
