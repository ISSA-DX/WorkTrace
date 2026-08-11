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

  // Auto-focus Staff ID field and handle auto-populate
  const staffInput = document.getElementById('staff_id');
  if (staffInput) {
    staffInput.focus();

    // Create a dynamic feedback div below Staff ID field
    const feedback = document.createElement('div');
    feedback.id = 'staff-id-feedback';
    feedback.className = 'field-hint';
    feedback.style.marginTop = '0.25rem';
    feedback.style.minHeight = '1.2rem';
    feedback.setAttribute('aria-live', 'polite');
    staffInput.parentNode.appendChild(feedback);

    let debounceTimeout;
    const checkStaffId = () => {
      const staffId = staffInput.value.trim();
      if (!staffId) {
        feedback.textContent = '';
        return;
      }

      fetch(`/api/employee/info/${encodeURIComponent(staffId)}`)
        .then(res => res.json())
        .then(data => {
          if (data.found) {
            feedback.textContent = `✓ Employee recognized: ${data.name}`;
            feedback.style.color = 'var(--success)';
            feedback.style.fontWeight = '600';

            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const positionInput = document.getElementById('position');

            if (nameInput) nameInput.value = data.name;
            if (emailInput) emailInput.value = data.email;
            if (positionInput && data.position) positionInput.value = data.position;
          } else {
            feedback.textContent = 'New employee (will be registered on submission)';
            feedback.style.color = 'var(--text-muted)';
            feedback.style.fontWeight = 'normal';
          }
        })
        .catch(err => console.error('Error fetching employee info:', err));
    };

    staffInput.addEventListener('input', () => {
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(checkStaffId, 300);
    });

    staffInput.addEventListener('blur', checkStaffId);
  }
});
