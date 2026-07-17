# Palette's Journal - Critical UX & Accessibility Learnings

This journal logs critical UX/accessibility learnings discovered while working on WorkTrace.

## 2026-05-24 - Frictionless QR Attendance Submission with LocalStorage
**Learning:** For web applications where end users scan public QR codes to clock in/out on their personal devices, requiring complete repetitive manual input of staff details (Name, ID, Email) on every scan creates a highly repetitive and error-prone user flow. Because they are not authenticated via a standard persistent user session on their mobile browser, standard local storage can act as a local lightweight profile cache to automatically pre-fill non-sensitive identification fields.
**Action:** Implement frontend local-storage state synchronization for form fields in unauthenticated QR-based scanning landing flows to drastically reduce manual repetitive inputs while keeping the backend authentication-free.
