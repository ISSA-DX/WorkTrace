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

  // Remember details on clock-in / clock-out forms
  const nameInput = document.getElementById('name');
  const staffIdInput = document.getElementById('staff_id');
  const positionInput = document.getElementById('position');
  const emailInput = document.getElementById('email');
  const rememberMeCheckbox = document.getElementById('remember_me');

  if (rememberMeCheckbox && nameInput && staffIdInput && emailInput) {
    // Check if saved details exist in localStorage
    const savedName = localStorage.getItem('wt_employee_name');
    const savedStaffId = localStorage.getItem('wt_employee_staff_id');
    const savedPosition = localStorage.getItem('wt_employee_position');
    const savedEmail = localStorage.getItem('wt_employee_email');

    if (savedName && savedStaffId && savedEmail) {
      if (!nameInput.value) nameInput.value = savedName;
      if (!staffIdInput.value) staffIdInput.value = savedStaffId;
      if (positionInput && !positionInput.value) positionInput.value = savedPosition || '';
      if (!emailInput.value) emailInput.value = savedEmail;
      rememberMeCheckbox.checked = true;
    }

    const form = rememberMeCheckbox.closest('form');
    if (form) {
      form.addEventListener('submit', () => {
        if (rememberMeCheckbox.checked) {
          localStorage.setItem('wt_employee_name', nameInput.value.trim());
          localStorage.setItem('wt_employee_staff_id', staffIdInput.value.trim());
          if (positionInput) {
            localStorage.setItem('wt_employee_position', positionInput.value.trim());
          }
          localStorage.setItem('wt_employee_email', emailInput.value.trim());
        } else {
          localStorage.removeItem('wt_employee_name');
          localStorage.removeItem('wt_employee_staff_id');
          localStorage.removeItem('wt_employee_position');
          localStorage.removeItem('wt_employee_email');
        }
      });
    }
  }
});
