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

  // Dynamic form submit loading states & prevent double submit
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        setTimeout(() => {
          submitBtn.disabled = true;
          const originalText = submitBtn.textContent;
          if (originalText.includes('Clock-In')) {
            submitBtn.textContent = 'Clocking In... ⏱';
          } else if (originalText.includes('Clock-Out')) {
            submitBtn.textContent = 'Clocking Out... ⏱';
          } else if (originalText.includes('Sign In')) {
            submitBtn.textContent = 'Signing In... ⏱';
          } else {
            submitBtn.textContent = 'Saving... ⏱';
          }
        }, 0);
      }
    });
  });
});
