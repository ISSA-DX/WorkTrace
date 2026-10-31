# Palette's Journal

## 2026-05-24 - Accessible Custom Checkbox & Toggle Switch Pattern
**Learning:** Custom toggle switches implemented via `.toggle-label input[type=checkbox] { display: none; }` completely remove the interactive control from keyboard focus order and assistive tech trees, preventing tab navigation and screen-reader announcements. Hiding the native `<input>` visually using `position: absolute; width: 1px; height: 1px; clip: rect(0,0,0,0); overflow: hidden;` keeps it focusable and interactive via standard spacebar/click bindings.
**Action:** Always visually hide checkbox inputs rather than using `display: none`, attach `:focus-visible` ring styles to the sibling `.toggle-slider`, and supply `role="switch"` and `aria-checked` attributes for accessible switch components.
