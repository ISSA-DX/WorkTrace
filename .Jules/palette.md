## 2025-02-22 - Dismissible Alert Close Button Accessibility

**Learning:** Flash notification close buttons with pure text/unicode characters (like "✕") lack accessible names for screen readers and explicit `type="button"` attributes, causing assistive technologies to miss their intent or default to form submission behaviors. Additionally, borderless icon buttons need explicit `:focus-visible` outlines so keyboard navigators can perceive focus.

**Action:** Always add `type="button"`, `aria-label="Dismiss alert"`, and explicit `:focus-visible` outlines to icon-only dismiss controls in alert/toast components.
