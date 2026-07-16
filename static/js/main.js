// WorkTrace — main.js

document.addEventListener('DOMContentLoaded', () => {
  // 1. Selective Alert Auto-Dismissal:
  // Only auto-dismiss success and info alerts; keep errors and warnings sticky.
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
      setTimeout(() => {
        alert.style.transition = 'opacity .4s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 400);
      }, 5000);
    }
  });

  // 2. Form Autofill via LocalStorage:
  // Pre-populate Clock-In and Clock-Out forms from previously saved details.
  const nameInput = document.getElementById('name');
  const staffIdInput = document.getElementById('staff_id');
  const positionInput = document.getElementById('position');
  const emailInput = document.getElementById('email');

  if (nameInput && staffIdInput) {
    if (!nameInput.value && localStorage.getItem('worktrace_name')) {
      nameInput.value = localStorage.getItem('worktrace_name');
    }
    if (!staffIdInput.value && localStorage.getItem('worktrace_staff_id')) {
      staffIdInput.value = localStorage.getItem('worktrace_staff_id');
    }
    if (positionInput && !positionInput.value && localStorage.getItem('worktrace_position')) {
      positionInput.value = localStorage.getItem('worktrace_position');
    }
    if (emailInput && !emailInput.value && localStorage.getItem('worktrace_email')) {
      emailInput.value = localStorage.getItem('worktrace_email');
    }

    const form = nameInput.closest('form');
    if (form) {
      form.addEventListener('submit', (e) => {
        if (e.defaultPrevented) return;
        localStorage.setItem('worktrace_name', nameInput.value.trim());
        localStorage.setItem('worktrace_staff_id', staffIdInput.value.trim().toUpperCase());
        if (positionInput) {
          localStorage.setItem('worktrace_position', positionInput.value.trim());
        }
        if (emailInput) {
          localStorage.setItem('worktrace_email', emailInput.value.trim());
        }
      });
    }
  }

  // 3. Form Submission Feedback & Double-Submit Protection:
  // Disable submit buttons on form submission to prevent double submission.
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      if (e.defaultPrevented) return;
      if (form.checkValidity && !form.checkValidity()) return;

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        setTimeout(() => {
          submitBtn.disabled = true;
          submitBtn.innerHTML = 'Submitting...';
        }, 0);
      }
    });
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
});
