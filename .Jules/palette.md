## 2026-10-11 - Accessible Icon Buttons and Focus Ring Indicators
**Learning:** Close buttons represented by unicode symbols (like `✕`) and abbreviated action buttons (like `Del`) lack semantic meaning for screen readers, while custom focus styles on inputs alone leave buttons without clear keyboard focus indicators.
**Action:** Always provide explicit `aria-label` attributes on symbol/abbreviated buttons and include global `:focus-visible` ring styling in `style.css` alongside a skip-to-content link for seamless keyboard and screen reader navigation.
