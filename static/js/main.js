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

  // Handle form submissions with loading text and spinner on buttons
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[data-loading-text], input[type="submit"][data-loading-text]');
      if (submitBtn) {
        const loadingText = submitBtn.getAttribute('data-loading-text');

        // Prevent multiple submissions by disabling the button/form
        setTimeout(() => {
          submitBtn.disabled = true;
        }, 10);

        // Inject inline SVG spinner and loading text
        submitBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 50 50" style="animation: spin 1s linear infinite; margin-right: 6px; display: inline-block; vertical-align: middle;">
            <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="80 150" stroke-linecap="round"></circle>
          </svg>
          <span>${loadingText}</span>
        `;
      }
    });
  });
});
