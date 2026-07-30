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

  // Auto-fill and persist employee details in clock-in/out forms
  const clockInForm = document.querySelector('form[action*="clock-in"]');
  const clockOutForm = document.querySelector('form[action*="clock-out"]');
  const form = clockInForm || clockOutForm;

  if (form) {
    const fields = ['staff_id', 'name', 'position', 'email'];
    // Pre-fill fields from localStorage if they are empty
    fields.forEach(field => {
      const input = form.querySelector(`#${field}`);
      if (input && !input.value) {
        const storedValue = localStorage.getItem(`worktrace_${field}`);
        if (storedValue) {
          input.value = storedValue;
        }
      }
    });

    // Persist fields to localStorage on form submit
    form.addEventListener('submit', () => {
      fields.forEach(field => {
        const input = form.querySelector(`#${field}`);
        if (input && input.value) {
          localStorage.setItem(`worktrace_${field}`, input.value.trim());
        }
      });
    });
  }
});
