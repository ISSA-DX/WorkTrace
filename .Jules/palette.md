# Palette's Journal - Critical Learnings

## 2025-05-24 - Focus Visible & Flash Alert Accessibility
**Learning:** Dismissible flash alerts with icon-only close buttons (like "✕") need clear `aria-label` attributes for screen readers, and interactive elements across navigation bar, sidebar links, and action buttons need distinct `:focus-visible` styling for keyboard navigation.
**Action:** Always verify icon-only buttons have `aria-label` and global button/link selectors support `:focus-visible` ring/outline states without altering element layout.
