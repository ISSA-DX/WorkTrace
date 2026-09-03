## 2025-05-18 - Accessible Toggles and Dismiss Buttons
**Learning:** Custom toggle switches using `display: none` on native `<input type="checkbox">` hide interactive elements from keyboard focus and screen readers completely.
**Action:** Use a visually-hidden CSS pattern (`clip: rect(0,0,0,0)`) on custom checkboxes and apply `:focus-visible` styles to the target adjacent slider/label so keyboard users can navigate and toggle seamlessly.
