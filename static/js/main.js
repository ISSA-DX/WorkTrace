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

  // Provide feedback on form submission and prevent duplicates
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (e.defaultPrevented) return;

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        // Disable button immediately after click/submit to prevent duplicate submissions
        setTimeout(() => {
          submitBtn.disabled = true;
          // Store original text
          submitBtn.dataset.originalText = submitBtn.innerHTML;
          // Set loading text
          if (form.action.includes('clock-in')) {
            submitBtn.innerHTML = 'Clocking In...';
          } else if (form.action.includes('clock-out')) {
            submitBtn.innerHTML = 'Clocking Out...';
          } else {
            submitBtn.innerHTML = 'Submitting...';
          }
        }, 0);
      }
    });
  });
});
