## 2025-05-18 - Accessible Custom Toggles & Interactive Focus States

**Learning:** Hiding custom checkboxes with `display: none` completely removes them from the accessibility tree and keyboard tab flow, preventing keyboard and screen-reader users from toggling settings.
**Action:** Use visually-hidden CSS (`position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;`) for underlying inputs and style `.toggle-label input:focus-visible + .toggle-slider` with explicit `:focus-visible` outline indicators.
