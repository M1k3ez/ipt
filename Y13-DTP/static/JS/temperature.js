document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const elements = document.querySelectorAll('.element');
    const resetButton = document.getElementById('reset-temperature');

    // Constants from Flask
    const MIN_TEMPERATURE = parseInt(document.getElementById('min-temp').textContent);
    const MAX_TEMPERATURE = parseInt(document.getElementById('max-temp').textContent);
    const NORM_TEMPERATURE = parseInt(document.getElementById('norm-temp').textContent);

    // Set min and max attributes for the slider
    temperatureSlider.min = MIN_TEMPERATURE;
    temperatureSlider.max = MAX_TEMPERATURE;

    let lastValidTemperature = parseInt(temperatureSlider.value); // Store the last valid temperature value

    function validateTemperature(temperature) {
        return temperature >= MIN_TEMPERATURE && temperature <= MAX_TEMPERATURE;
    }

    function updateTemperature(value) {
        const temperature = parseInt(value);
        if (!validateTemperature(temperature)) {
            // Ignore invalid value without reverting or updating the slider
            return;
        }

        lastValidTemperature = temperature; // Update last valid temperature
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

    // Prevent invalid values from being entered in the slider
    temperatureSlider.addEventListener('input', function() {
        const value = parseInt(this.value);
        if (validateTemperature(value)) {
            updateTemperature(value);
        } else {
            this.value = lastValidTemperature; // Ignore the invalid value and stay at the last valid value
        }
    });

    temperatureSlider.addEventListener('change', function() {
        const value = parseInt(this.value);
        if (validateTemperature(value)) {
            updateTemperature(value);
        } else {
            this.value = lastValidTemperature; // Ignore the invalid value and stay at the last valid value
        }
    });

    resetButton.addEventListener('click', function() {
        temperatureSlider.value = NORM_TEMPERATURE;
        updateTemperature(NORM_TEMPERATURE);
    });

    // Initial validation and setting
    updateTemperature(temperatureSlider.value);
});
