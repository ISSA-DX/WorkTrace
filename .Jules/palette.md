## 2026-08-15 - ARIA Labels for Action Buttons in Data Tables
**Learning:** Table action buttons with repeated text labels (e.g. 'Edit', 'Delete', 'Approve', 'PDF') lack context for screen readers when navigating out of table context.
**Action:** Always include contextual `aria-label` attributes incorporating the entity name or identifier (e.g. `aria-label="Edit employee {{ emp.name }}"`).
