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

  // Handle "Remember my details on this device" for clock-in/out forms
  const isClockForm = document.querySelector('.form-header-in, .form-header-out');
  if (isClockForm) {
    const rememberMeCheckbox = document.getElementById('remember_me');
    const fields = ['name', 'staff_id', 'position', 'email'];

    // Load saved details on page load
    const shouldRemember = localStorage.getItem('worktrace_remember_me') === 'true';
    if (rememberMeCheckbox) {
      rememberMeCheckbox.checked = shouldRemember;
      if (shouldRemember) {
        fields.forEach(fieldId => {
          const val = localStorage.getItem('worktrace_' + fieldId);
          const el = document.getElementById(fieldId);
          if (val && el) {
            el.value = val;
          }
        });
      }
    }

    // Save or clear on form submit
    const form = isClockForm.closest('.form-card')?.querySelector('form');
    if (form) {
      form.addEventListener('submit', () => {
        if (rememberMeCheckbox && rememberMeCheckbox.checked) {
          localStorage.setItem('worktrace_remember_me', 'true');
          fields.forEach(fieldId => {
            const el = document.getElementById(fieldId);
            if (el) {
              localStorage.setItem('worktrace_' + fieldId, el.value.trim());
            }
          });
        } else {
          localStorage.setItem('worktrace_remember_me', 'false');
          fields.forEach(fieldId => {
            localStorage.removeItem('worktrace_' + fieldId);
          });
        }
      });
    }
  }
});
