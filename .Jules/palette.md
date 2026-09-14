## 2025-05-24 - Flash Alert Dismiss Button Accessibility & Global Focus States
**Learning:** Dismiss buttons with icon-only characters like "✕" need explicit `type="button"` and `aria-label` so screen readers announce their purpose. Additionally, adding `:focus-visible` styles ensures keyboard users can visually identify focused interactive controls across the interface.
**Action:** Always include `type="button"` and `aria-label` on dismiss/icon-only buttons, and pair with `:focus-visible` styles in global CSS.
