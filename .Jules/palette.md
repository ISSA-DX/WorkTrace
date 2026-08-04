# Palette's Journal

## 2026-05-24 - Device-Aware Auto-Fill & Privacy Control
**Learning:** In multi-user employee management environments, automatically pre-filling or caching credentials on shared kiosks/terminals without user consent leads to severe UX hazards and accidental duplicate clock-ins/outs under wrong identities. Providing an explicit opt-in toggle ("Remember my details on this device") is essential to balance high accessibility (for personal devices) with strict separation and privacy (for shared devices).
**Action:** For repeat form entries on employee-facing applications, always implement `localStorage` pre-filling behind an explicit, accessible opt-in toggle rather than automatically caching entries.
