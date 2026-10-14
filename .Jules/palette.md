## 2025-05-24 - Visually Hidden Toggle Inputs for Keyboard & Screen Reader Access
**Learning:** Using `display: none` on custom styled checkbox inputs (like toggle switches) completely hides them from accessibility trees and keyboard focus navigation, rendering them inaccessible to screen readers and keyboard users.
**Action:** Always use a CSS clip pattern or visually-hidden utility classes for form inputs paired with custom visual elements, and ensure `:focus-visible` styles are provided on the adjacent visible slider element.
