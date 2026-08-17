## 2025-05-24 - Accessible Custom Checkbox Toggle Switches
**Learning:** Hiding `<input type="checkbox">` using `display: none` completely removes it from the accessibility tree and keyboard navigation flow, rendering custom toggles inaccessible to screen reader and keyboard-only users.
**Action:** Use a `.visually-hidden` technique (clip/absolute positioning with zero dimensions) on the input and style `:focus-visible + .toggle-slider` to show a clear outline when focused via keyboard.
