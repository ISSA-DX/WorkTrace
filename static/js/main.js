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
  const nameInput = document.getElementById('name');
  const staffIdInput = document.getElementById('staff_id');
  const positionInput = document.getElementById('position');
  const emailInput = document.getElementById('email');

  if (nameInput || staffIdInput || positionInput || emailInput) {
    // Load from localStorage if the form fields are currently empty
    if (nameInput && !nameInput.value) nameInput.value = localStorage.getItem('wt_name') || '';
    if (staffIdInput && !staffIdInput.value) staffIdInput.value = localStorage.getItem('wt_staff_id') || '';
    if (positionInput && !positionInput.value) positionInput.value = localStorage.getItem('wt_position') || '';
    if (emailInput && !emailInput.value) emailInput.value = localStorage.getItem('wt_email') || '';

    // Save on form submit
    const forms = document.querySelectorAll('.form-card form');
    forms.forEach(form => {
      form.addEventListener('submit', () => {
        if (nameInput && nameInput.value) localStorage.setItem('wt_name', nameInput.value.trim());
        if (staffIdInput && staffIdInput.value) localStorage.setItem('wt_staff_id', staffIdInput.value.trim().toUpperCase());
        if (positionInput && positionInput.value) localStorage.setItem('wt_position', positionInput.value.trim());
        if (emailInput && emailInput.value) localStorage.setItem('wt_email', emailInput.value.trim().toLowerCase());
      });
    });
  }
});
