# Palette's UX & Accessibility Journal

## 2026-05-24 - Selective Alert Auto-Dismissal and Local Form Auto-Fill
**Learning:** Automatically dismissing alerts can lead to significant accessibility issues when they contain critical warnings or errors, as users might miss them entirely. Only success or non-critical messages should be auto-dismissed. Additionally, on mobile-first QR web workflows, requiring users to repeat detailed form entries (like Name, Staff ID, position, email) on every transaction increases cognitive load and user fatigue. Using local storage to safely preserve and autofill employee profiles is an elegant, privacy-first UX pattern.
**Action:** Always filter flash messages by severity before setting auto-dismiss timers, keeping errors sticky. Always identify repeat form patterns on transactional QR entry flows and offer client-side persistence (like localStorage) to minimize user friction.
