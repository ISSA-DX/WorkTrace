// WorkTrace — main.js

// Auto-dismiss flash alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Only auto-dismiss non-critical alerts (success, info).
    // Do not auto-dismiss errors/warnings, they require explicit manual dismissal.
    const isCritical = alert.classList.contains('alert-error') ||
                       alert.classList.contains('alert-warning') ||
                       alert.classList.contains('alert-danger');
    if (!isCritical) {
      let timeLeft = 5000;
      let isPaused = false;
      let lastTick = Date.now();

      const tick = () => {
        if (!alert.isConnected) return; // Terminate loop if alert is removed
        if (!isPaused) {
          const now = Date.now();
          timeLeft -= (now - lastTick);
          lastTick = now;
          if (timeLeft <= 0) {
            alert.style.transition = 'opacity .4s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 400);
            return;
          }
        } else {
          lastTick = Date.now();
        }
        requestAnimationFrame(tick);
      };

      // Pause when user hovers or focuses on the alert, resume when they leave.
      alert.addEventListener('mouseenter', () => { isPaused = true; });
      alert.addEventListener('mouseleave', () => { isPaused = false; });
      alert.addEventListener('focusin', () => { isPaused = true; });
      alert.addEventListener('focusout', () => { isPaused = false; });

      requestAnimationFrame(tick);
    }
  });

  // Set datetime-local max to now + 15 min for clock-in
  const dtInputs = document.querySelectorAll('input[type="datetime-local"]');
  dtInputs.forEach(input => {
    if (!input.max) {
      const max = new Date(Date.now() + 15 * 60000);
      input.max = max.toISOString().slice(0, 16);
    }
  });

  // Confirm delete forms
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', e => {
      if (!confirm(btn.dataset.confirm)) e.preventDefault();
    });
  });
});
