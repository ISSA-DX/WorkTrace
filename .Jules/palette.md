# Palette's Journal — Critical UX & Accessibility Learnings

## 2026-05-24 - Beautiful Focus Rings & Descriptive Form Controls
**Learning:**
1. Traditional visual focus-ring styles (outline: none) inside CSS sheets strip away vital access for keyboard-navigating users without developers noticing. Utilizing `:focus-visible` ensures that only interactive elements focused via keyboard receive a clear, high-contrast visual outline, avoiding clutter for click/pointer actions.
2. Form required symbols such as asterisks (`*`) are often read out loud by screen readers as "asterisk" or "multiplication sign" instead of providing useful info. Placing `aria-hidden="true"` on the symbol and attaching `aria-required="true"` to the underlying input provides a clear and professional accessibility footprint.
3. Alert or flash close buttons with raw symbols (like `✕` or `X`) are highly ambiguous for screen-reader users unless they explicitly declare their interactive role and purpose using `type="button"` and `aria-label="Dismiss alert"`.

**Action:**
1. Always avoid `outline: none` without a corresponding `:focus-visible` backup. Define generic, high-contrast, beautiful `:focus-visible` borders tailored to the theme's highlight color palette.
2. Hide visual-only mandatory/required flags (`*`) from screen readers with `aria-hidden="true"`, and directly use `aria-required="true"` on the input tags.
3. Equip close, dismiss, delete, or edit buttons that only display icons or text symbols with clean `aria-label` declarations.
