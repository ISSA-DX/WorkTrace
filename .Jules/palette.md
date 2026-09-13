## 2025-05-24 - Accessibility Enhancements for Flash Alerts & Navigation

**Learning:** Flash alert dismiss buttons using icon characters (`✕`) lacked accessible names (`aria-label`), making them opaque to screen reader users. Active navigation links lacked `aria-current="page"`, and global `:focus-visible` outlines were missing for keyboard navigation.

**Action:** Always provide explicit `aria-label` for icon-only action buttons, mark active page links with `aria-current="page"`, and include global `:focus-visible` styles using design tokens (`var(--accent)`).
