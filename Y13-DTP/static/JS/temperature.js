document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const elements = document.querySelectorAll('.element');
    const resetButton = document.getElementById('reset-temperature');

    function updateTemperature(value) {
        const temperature = parseInt(value);
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

    temperatureSlider.addEventListener('input', function() {
        updateTemperature(this.value);
    });

    resetButton.addEventListener('click', function() {
        temperatureSlider.value = 273;
        updateTemperature(273);
    });

    temperatureSlider.dispatchEvent(new Event('input'));
});
