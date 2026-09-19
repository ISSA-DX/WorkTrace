## 2025-05-24 - Screen Reader Context & Focus Indicators
**Learning:** Abbreviated and icon buttons (like "Del" or "✕") need contextual `aria-label` attributes for screen readers, and interactive controls without `:focus-visible` styles leave keyboard navigation invisible.
**Action:** Provide explicit `aria-label` attributes specifying target context on action buttons and alert close controls, and define `:focus-visible` outline styles in CSS.
