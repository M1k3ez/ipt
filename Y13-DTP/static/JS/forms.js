document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('contact_form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        clearNotifications(); // Function to clear existing notifications

        const email = form.querySelector('input[name="email"]').value;
        if (!isValidEmailFormat(email)) {
            showFlashMessage('Invalid email.', 'danger');
            return;
        }
        if (!isDesiredDomain(email)) {
            showFlashMessage('Please use email from Yahoo, Google or Outlook.', 'danger');
            return;
        }

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);

        submitFormData(data);
    });

    function clearNotifications() {
        document.querySelectorAll('.notification').forEach(el => el.remove());
    }

    function isValidEmailFormat(email) {
        // Regex to match the email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isDesiredDomain(email) {
        const domain = email.split('@')[1];
        const allowedDomains = ["gmail.com", "yahoo.com", "outlook.com"];
        const isAllowedDomain = allowedDomains.includes(domain) || domain.includes('.edu') || domain.includes('.uni') || domain.includes('.school');
        return isAllowedDomain;
    }

    function submitFormData(data) {
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            clearNotifications();
            if (data.errors) {
                data.errors.forEach(error => {
                    showFlashMessage(`Error in ${error.field}: ${error.message}`, 'danger');
                });
            } else {
                showFlashMessage(data.message, data.category);
            }
        })
        .catch(error => {
            clearNotifications();
            showFlashMessage('An error occurred. Please try again.', 'danger');
        });
    }
});
