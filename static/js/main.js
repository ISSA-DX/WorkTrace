// WorkTrace — main.js

// Auto-dismiss flash alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
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

  // Pre-fill and persist clock-in / clock-out forms from localStorage
  const persistFields = ['name', 'staff_id', 'position', 'email'];
  const clockForm = document.querySelector('form[action*="clock-in"], form[action*="clock-out"]');
  if (clockForm) {
    persistFields.forEach(fieldId => {
      const input = clockForm.querySelector(`#${fieldId}`);
      if (input && !input.value) {
        const saved = localStorage.getItem(`worktrace_${fieldId}`);
        if (saved) input.value = saved;
      }
    });

    clockForm.addEventListener('submit', () => {
      persistFields.forEach(fieldId => {
        const input = clockForm.querySelector(`#${fieldId}`);
        if (input) {
          localStorage.setItem(`worktrace_${fieldId}`, input.value.trim());
        }
      });
    });
  }
});
