## 2025-05-20 - Toggle Switch Keyboard Focus & Accessibility
**Learning:** Hiding checkbox inputs with `display: none` in custom toggle controls breaks screen reader accessibility and keyboard focus states. Using a visually-hidden utility pattern (opacity 0, absolute position) allows the native checkbox to remain focusable while preserving custom slider visuals on `:focus-visible`.
**Action:** Always replace `display: none` on input controls with a visually hidden clip/opacity pattern and style `.toggle-slider` or label when `input:focus-visible`.
