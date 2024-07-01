document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const elements = document.querySelectorAll('.element');
    const resetButton = document.getElementById('reset-temperature');
    function updateTemperature(value) {
        const temperature = parseInt(value);
        temperatureValue.textContent = `${temperature} K`;
        elements.forEach(element => {
            const meltingPoint = parseInt(element.getAttribute('data-melting'));
            const boilingPoint = parseInt(element.getAttribute('data-boiling'));

            if (isNaN(meltingPoint) || isNaN(boilingPoint)) {
                element.style.border = '2px dotted gray';
                return;
            }
            if (temperature < meltingPoint) {
                element.style.border = '2px double black'; // Solid
            } else if (temperature >= meltingPoint && temperature < boilingPoint) {
                element.style.border = '2px solid black'; // Liquid
            } else if (temperature >= boilingPoint) {
                element.style.border = '2px dashed black'; // Gas
            } else {
                element.style.border = '2px dotted black'; // Unknown
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
