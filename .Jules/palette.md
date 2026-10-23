## 2026-10-23 - Accessible Table Action Labels & Focus Visibility

**Learning:** Repetitive table action buttons (e.g., "Edit", "Delete", "Approve", "PDF") lack screen-reader context when read out of document order, and native outline styles may be reset or weak without explicit `:focus-visible` styling.

**Action:** Always include contextual `aria-label` attributes on table row action buttons with the entity name/ID and define clean, high-visibility `:focus-visible` ring styles.
