document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const elements = document.querySelectorAll('.element');
    const resetButton = document.getElementById('reset-temperature');

    // Constants from Flask
    const MIN_TEMPERATURE = parseInt(document.getElementById('min-temp').textContent);
    const MAX_TEMPERATURE = parseInt(document.getElementById('max-temp').textContent);
    const NORM_TEMPERATURE = parseInt(document.getElementById('norm-temp').textContent);

    // Use the 404 route URL from Flask
    const notFoundRoute = '/404'; 

    function validateTemperature(temperature) {
        if (temperature < MIN_TEMPERATURE || temperature > MAX_TEMPERATURE) {
            window.location.href = notFoundRoute;
            return false;
        }
        return true;
    }

    function updateTemperature(value) {
        const temperature = parseInt(value);
        if (!validateTemperature(temperature)) {
            temperatureSlider.value = NORM_TEMPERATURE; // Reset to a valid value to prevent further issues
            return;
        }

        temperatureValue.textContent = `${temperature} K`;
        elements.forEach(element => {
            const meltingPoint = element.getAttribute('data-melting');
            const boilingPoint = element.getAttribute('data-boiling');

            // Remove existing state classes
            element.classList.remove('solid', 'liquid', 'gas', 'unknown');

            const hasValidMeltingPoint = meltingPoint !== 'N/A' && !isNaN(parseInt(meltingPoint));
            const hasValidBoilingPoint = boilingPoint !== 'N/A' && !isNaN(parseInt(boilingPoint));

            if (!hasValidMeltingPoint && !hasValidBoilingPoint) {
                element.classList.add('unknown');
                return;
            }

            if (hasValidMeltingPoint && temperature < parseInt(meltingPoint)) {
                element.classList.add('solid'); // Solid
            } else if (hasValidMeltingPoint && hasValidBoilingPoint && temperature >= parseInt(meltingPoint) && temperature < parseInt(boilingPoint)) {
                element.classList.add('liquid'); // Liquid
            } else if (hasValidBoilingPoint && temperature >= parseInt(boilingPoint)) {
                element.classList.add('gas'); // Gas
            } else {
                element.classList.add('unknown'); // Unknown
            }
        });
    }

    // Check for long element names and adjust font size if necessary
    function adjustElementNameFontSize() {
        const elementNames = document.querySelectorAll('.element-name');
        elementNames.forEach(function (element) {
            const maxLength = 9; // Adjust this value based on your design needs
            if (element.textContent.length > maxLength) {
                element.classList.add('small-font'); // Add the small-font class
            }
        });
    }

    // Handle changes through user interaction and direct console manipulation
    temperatureSlider.addEventListener('input', function() {
        updateTemperature(this.value);
    });

    temperatureSlider.addEventListener('change', function() {
        updateTemperature(this.value);
    });

    resetButton.addEventListener('click', function() {
        temperatureSlider.value = NORM_TEMPERATURE;
        updateTemperature(NORM_TEMPERATURE);
    });

    // Initial validation and setting
    updateTemperature(temperatureSlider.value);

    // Adjust font size of element names on page load
    adjustElementNameFontSize();
});
