# Palette's Journal - Critical UX/Accessibility Learnings

This journal tracks critical learnings discovered regarding accessibility patterns, surprising user behavior, and design system constraints specific to this app.

## 2026-07-18 - [Accessible Custom Checkbox Toggles]
**Learning:** Overwriting or hiding interactive elements using `display: none` completely breaks screen-reader accessibility and keyboard-only focus navigation. Instead, hiding checkboxes using an absolute position, clip, and tiny footprint allows them to remain visible to screen readers and receive native keyboard focus. We can then style a companion element using `input:focus-visible + .toggle-slider` to show a beautiful focus ring for keyboard users.
**Action:** Always avoid `display: none` on interactive form fields. Instead, use visually-hidden styles and forward focus styles to custom visual representations.
