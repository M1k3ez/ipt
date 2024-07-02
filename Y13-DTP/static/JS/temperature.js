document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature-slider');
    const temperatureValue = document.getElementById('temperature-value');
    const elements = document.querySelectorAll('.element');
    const resetButton = document.getElementById('reset-temperature');
    function updateTemperature(value) {
        const temperature = parseInt(value); // Convert value to integer
        temperatureValue.textContent = `${temperature} K`; // Update temperature display
        // Redirect to 404 page if temperature is out of bounds
        if (temperature < -273 || temperature > 700) {
            window.location.href = '/404.html';
            return;
        }
        // Update element borders based on temperature
        elements.forEach(element => {
            const meltingPoint = parseInt(element.getAttribute('data-melting'));
            const boilingPoint = parseInt(element.getAttribute('data-boiling'));
            // Handle cases where melting or boiling points are not numbers
            if (isNaN(meltingPoint) || isNaN(boilingPoint)) {
                element.style.border = '2px dotted gray';
                return;
            }
            // Set border style based on temperature relative to melting and boiling points
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
        updateTemperature(this.value); // Update temperature on slider input
    });
    resetButton.addEventListener('click', function() {
        temperatureSlider.value = 273; // Reset slider to 273 K
        updateTemperature(273); // Update temperature display and element states
    });
    // Trigger input event to initialize temperature display and element states
    temperatureSlider.dispatchEvent(new Event('input'));
});
