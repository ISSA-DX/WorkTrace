## 2026-09-07 - Focus-Visible States & Skip Link for Key Public Templates
**Learning:** Dismiss buttons on alert notifications and navbar/sidebar links in base HTML templates were missing keyboard focus rings and `aria-label` tags, hindering screen reader users and keyboard navigation.
**Action:** Always include `.skip-link` in main layouts, add `:focus-visible` ring styles to interactive elements in `style.css`, and ensure all icon-only buttons (`.alert-close`) have explicit `aria-label` attributes.
