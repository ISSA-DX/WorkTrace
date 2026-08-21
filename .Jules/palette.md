## 2025-05-24 - Interactive Elements Accessibility & Keyboard Focus
**Learning:** Icon-only buttons (like `.alert-close`) and standard buttons across Flask template apps missing `aria-label` or explicit focus-visible focus rings degrade keyboard navigation and screen reader experience.
**Action:** Always add `aria-label` to icon-only buttons, ensure focus-visible states use clear outlines, and maintain changes under 50 lines without extra CSS frameworks or tokens.
