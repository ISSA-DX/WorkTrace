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

  // Autofill and remember details for Clock-In / Clock-Out
  const clockForm = document.getElementById('clock-form');
  if (clockForm) {
    const fields = ['staff_id', 'name', 'position', 'email'];
    const rememberMe = document.getElementById('remember_me');
    const savedRemember = localStorage.getItem('worktrace_remember');

    // Default to true if not set
    const shouldRemember = savedRemember !== 'false';
    if (rememberMe) {
      rememberMe.checked = shouldRemember;
    }

    if (shouldRemember) {
      fields.forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (input && !input.value) {
          const savedVal = localStorage.getItem('worktrace_' + fieldId);
          if (savedVal) {
            input.value = savedVal;
          }
        }
      });
    }

    clockForm.addEventListener('submit', () => {
      const isChecked = rememberMe ? rememberMe.checked : false;
      localStorage.setItem('worktrace_remember', isChecked ? 'true' : 'false');
      fields.forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (input) {
          if (isChecked) {
            localStorage.setItem('worktrace_' + fieldId, input.value.trim());
          } else {
            localStorage.removeItem('worktrace_' + fieldId);
          }
        }
      });
    });
  }
});
