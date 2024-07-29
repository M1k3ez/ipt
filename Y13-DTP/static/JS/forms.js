// form.js
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('contact_form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.errors) {
                data.errors.forEach(error => {
                    showFlashMessage(`Error in ${error.field}: ${error.message}`, data.category);
                });
            } else {
                showFlashMessage(data.message, data.category);
            }
        })
        .catch(error => {
            showFlashMessage('An error occurred. Please try again.', 'danger');
        });
    });
});
