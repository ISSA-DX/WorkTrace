## 2025-05-18 - Keyboard Focus States and Icon-Only Alert Close Buttons

**Learning:** Interactive elements (`.btn`, `.sidebar-link`, `.alert-close`, links) in WorkTrace lacked explicit `:focus-visible` styles, hindering keyboard navigation accessibility. Additionally, the flash alert close buttons (`✕`) were icon-only without `aria-label` or explicit `type="button"` attributes, making them inaccessible to screen readers.

**Action:** Always include explicit `:focus-visible` outline styles for custom interactive elements and ensure all icon-only buttons feature descriptive `aria-label` attributes and explicit `type="button"` declarations.
