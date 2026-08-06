## 2026-08-06 - Decorative Emojis and Table Action Accessibility
**Learning:**
1. Using raw emojis as decorative icons or status badges (e.g., ⏱, 🟢, 🔴, 👥) without `aria-hidden="true"` causes screen readers to read out their literal descriptions (e.g., "green circle"), which clutters screen reader output and confuses context.
2. Large tabular datasets with multiple generic action buttons (like "Del", "Edit", "PDF") are screen-reader unfriendly unless given descriptive context-aware `aria-label` properties (e.g., "Delete record for John Smith on Aug 06, 2026").

**Action:**
- Always wrap decorative emojis in a span/element with `aria-hidden="true"`.
- Provide specific context in `aria-label` attributes for buttons inside rows of a loop/table.
