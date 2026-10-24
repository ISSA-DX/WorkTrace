## 2026-10-24 - Flash alert close button accessibility and keyboard focus indicators
**Learning:** Icon-only close buttons (e.g., '✕') on flash alert containers require explicit `aria-label` attributes to be navigable and announced properly by screen readers, and `:focus-visible` styles ensure focus rings are visible during keyboard tab navigation.
**Action:** Always include `aria-label="Dismiss alert"` on icon-only close buttons and pair with CSS `:focus-visible` outline styles for keyboard interaction.
