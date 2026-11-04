/**
 * Vehicle Service Management System
 * Client-side Form Validation
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Generic form validation with Bootstrap validation states
  const forms = document.querySelectorAll('.needs-validation');

  Array.from(forms).forEach(function (form) {
    form.addEventListener('submit', function (event) {
      let customValid = true;

      // Validate Phone (10 digits)
      const phoneInput = form.querySelector('input[name="phone"]');
      if (phoneInput) {
        const phoneRegex = /^[0-9]{10}$/;
        const val = phoneInput.value.trim();
        if (!phoneRegex.test(val)) {
          phoneInput.classList.add('is-invalid');
          customValid = false;
        } else {
          phoneInput.classList.remove('is-invalid');
          phoneInput.classList.add('is-valid');
        }
      }

      // Validate Password length (>= 6)
      const passwordInput = form.querySelector('input[name="password"]');
      if (passwordInput && passwordInput.hasAttribute('required')) {
        if (passwordInput.value.length < 6) {
          passwordInput.classList.add('is-invalid');
          customValid = false;
        } else {
          passwordInput.classList.remove('is-invalid');
          passwordInput.classList.add('is-valid');
        }
      }

      // Validate Vehicle Year (1980 - current year + 1)
      const yearInput = form.querySelector('input[name="year"]');
      if (yearInput) {
        const yearVal = parseInt(yearInput.value, 10);
        const currentYear = new Date().getFullYear();
        if (isNaN(yearVal) || yearVal < 1980 || yearVal > currentYear + 1) {
          yearInput.classList.add('is-invalid');
          customValid = false;
        } else {
          yearInput.classList.remove('is-invalid');
          yearInput.classList.add('is-valid');
        }
      }

      // Preferred date validation (cannot be in the past)
      const dateInput = form.querySelector('input[name="preferred_date"]');
      if (dateInput) {
        const selectedDate = new Date(dateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
          dateInput.classList.add('is-invalid');
          customValid = false;
        } else {
          dateInput.classList.remove('is-invalid');
          dateInput.classList.add('is-valid');
        }
      }

      if (!form.checkValidity() || !customValid) {
        event.preventDefault();
        event.stopPropagation();
      }

      form.classList.add('was-validated');
    }, false);
  });

  // 2. Real-time phone number formatting / sanitizing
  const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="phone"]');
  phoneInputs.forEach(input => {
    input.addEventListener('input', function () {
      this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
    });
  });

  // 3. Set minimum date for preferred_date inputs to today
  const preferredDateInputs = document.querySelectorAll('input[type="date"][name="preferred_date"]');
  if (preferredDateInputs.length > 0) {
    const todayStr = new Date().toISOString().split('T')[0];
    preferredDateInputs.forEach(input => {
      input.setAttribute('min', todayStr);
      if (!input.value) {
        input.value = todayStr;
      }
    });
  }
});
