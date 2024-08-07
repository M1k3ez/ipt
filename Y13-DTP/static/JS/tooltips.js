document.addEventListener('DOMContentLoaded', function () {
    const tooltips = document.querySelectorAll('.tooltip');

    tooltips.forEach(tooltip => {
        const column = parseInt(tooltip.style.gridColumn.split(' /')[0], 10);

        if (column === 1) {
            tooltip.classList.add('tooltip-left-edge');
        } else if (column === 18) {
            tooltip.classList.add('tooltip-right-edge');
        }

        const elementId = tooltip.getAttribute('data-id');
        if (elementId === '104' || elementId === '88') {
            tooltip.classList.add('tooltip-down');
        }
    });
});
