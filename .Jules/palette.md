# Palette UX Journal

## 2026-11-02 - Accessible Custom Toggles & Interactive Focus Rings
**Learning:** In CSS-only toggle switches, using `display: none` on `<input type="checkbox">` completely removes the element from keyboard tab sequence and accessibility trees. Screen reader and keyboard users cannot navigate to or toggle the switch. Furthermore, dismiss buttons on alerts rendered with simple "✕" symbols without `aria-label` leave screen reader users without context on what the interactive button does.
**Action:** When building custom styled form controls (switches, custom radios, custom checkboxes), always use a visually-hidden CSS technique (`position: absolute; width: 1px; height: 1px; clip: rect(0,0,0,0); overflow: hidden`) instead of `display: none`, and always tie `:focus-visible` states to the adjacent visual element (`input:focus-visible + .toggle-slider`). Always ensure icon/symbol-only action buttons provide an explicit `aria-label` and visible focus states.
