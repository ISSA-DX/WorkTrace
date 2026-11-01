## 2026-05-24 - Accessible Toggle Switches & Focus States
**Learning:** Custom CSS toggle switches often hide native checkbox inputs using `display: none`. This strips the input completely out of the accessibility tree and keyboard tab order, preventing keyboard-only and screen reader users from accessing or toggling the control.
**Action:** Always hide the checkbox input visually with an accessible clip/zero-opacity pattern rather than `display: none`, and bind visible focus indicator rings using `:focus-visible + .toggle-slider`.
