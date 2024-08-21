document.addEventListener('DOMContentLoaded', function () {
    const tooltips = document.querySelectorAll('.tooltip');

    tooltips.forEach(tooltip => {
        const rect = tooltip.getBoundingClientRect();
        const computedStyle = window.getComputedStyle(tooltip);
        const gridColumnStart = parseInt(computedStyle.gridColumnStart, 10);

        // Apply specific classes based on grid position
        if (gridColumnStart === 2) {
            tooltip.classList.add('tooltip-left-edge'); // First column
        } else if (gridColumnStart === 19) {
            tooltip.classList.add('tooltip-right-edge'); // Last column
        }

        const elementId = tooltip.getAttribute('data-id');
        if (elementId === '104' || elementId === '88') {
            tooltip.classList.add('tooltip-down');
        }

        // Adjust tooltip if it's near screen boundaries
        if (rect.right > window.innerWidth) {
            tooltip.style.left = `${window.innerWidth - rect.width - 10}px`;
        }

        if (rect.left < 0) {
            tooltip.style.left = `10px`;
        }

        // Hover to increase z-index
        tooltip.addEventListener('mouseover', function () {
            tooltip.style.zIndex = '1000';  // Set a high z-index when hovering
        });

        // Reset z-index when hover ends
        tooltip.addEventListener('mouseout', function () {
            tooltip.style.zIndex = '';  // Reset z-index to default
        });
    });
});
