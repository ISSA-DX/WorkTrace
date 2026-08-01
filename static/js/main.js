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

  // Quick rest options sync for clock-out form
  const restOptions = document.querySelectorAll('.btn-rest-option');
  const restInput = document.getElementById('rest_minutes');
  if (restInput && restOptions.length > 0) {
    const syncRestButtons = () => {
      const val = restInput.value;
      restOptions.forEach(o => {
        if (o.dataset.minutes === val) {
          o.classList.remove('btn-outline');
          o.classList.add('btn-primary');
        } else {
          o.classList.remove('btn-primary');
          o.classList.add('btn-outline');
        }
      });
    };

    restOptions.forEach(opt => {
      opt.addEventListener('click', () => {
        restInput.value = opt.dataset.minutes;
        syncRestButtons();
      });
    });

    restInput.addEventListener('input', syncRestButtons);
    syncRestButtons();
  }

  // Force uppercase on Staff ID input
  const staffIdInput = document.getElementById('staff_id');
  if (staffIdInput) {
    staffIdInput.addEventListener('input', () => {
      staffIdInput.value = staffIdInput.value.toUpperCase();
    });
  }
});
