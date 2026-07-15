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

  // --- Palette UX: Auto-Fill and Local Storage ---
  const staffIdInput = document.getElementById('staff_id');
  const nameInput = document.getElementById('name');
  const positionInput = document.getElementById('position');
  const emailInput = document.getElementById('email');
  const form = document.querySelector('.form-card form');

  if (staffIdInput && nameInput && positionInput && emailInput) {
    // 1. Load from localStorage if available
    const savedStaffId = localStorage.getItem('worktrace_staff_id');
    const savedName = localStorage.getItem('worktrace_name');
    const savedPosition = localStorage.getItem('worktrace_position');
    const savedEmail = localStorage.getItem('worktrace_email');

    if (savedStaffId && !staffIdInput.value) staffIdInput.value = savedStaffId;
    if (savedName && !nameInput.value) nameInput.value = savedName;
    if (savedPosition && !positionInput.value) positionInput.value = savedPosition;
    if (savedEmail && !emailInput.value) emailInput.value = savedEmail;

    // Helper to auto-fill fields
    const fillDetails = (data) => {
      if (data.name) nameInput.value = data.name;
      if (data.position) positionInput.value = data.position;
      if (data.email) emailInput.value = data.email;

      // Highlight fields briefly to show they were auto-filled
      [nameInput, positionInput, emailInput].forEach(input => {
        input.style.transition = 'background-color 0.5s ease';
        input.style.backgroundColor = '#e6fffa'; // soft mint green
        setTimeout(() => {
          input.style.backgroundColor = '';
        }, 1000);
      });
    };

    // Keep track of the last looked up staff ID to prevent duplicate requests on both blur and change
    let lastFetchedStaffId = '';

    // 2. Fetch employee details when Staff ID changes
    const fetchEmployeeDetails = async () => {
      const staffId = staffIdInput.value.trim().toUpperCase();
      if (!staffId || staffId === lastFetchedStaffId) return;
      lastFetchedStaffId = staffId;

      try {
        const response = await fetch(`/api/employee-lookup/${encodeURIComponent(staffId)}`);
        if (response.ok) {
          const data = await response.json();
          if (data.found) {
            fillDetails(data);
          }
        }
      } catch (error) {
        console.error('Error fetching employee lookup:', error);
      }
    };

    staffIdInput.addEventListener('change', fetchEmployeeDetails);
    staffIdInput.addEventListener('blur', fetchEmployeeDetails);

    // 3. Save to localStorage when form is submitted successfully
    if (form) {
      form.addEventListener('submit', () => {
        if (staffIdInput.value && nameInput.value && emailInput.value) {
          localStorage.setItem('worktrace_staff_id', staffIdInput.value.trim());
          localStorage.setItem('worktrace_name', nameInput.value.trim());
          localStorage.setItem('worktrace_position', positionInput.value.trim());
          localStorage.setItem('worktrace_email', emailInput.value.trim());
        }
      });
    }
  }
});
