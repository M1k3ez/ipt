$(document).ready(function() {
    // Event handler for element link click
    $('.element-link').click(function(event) {
        event.preventDefault(); // Prevent default link behavior
        var electronNumber = $(this).data('id');
        // Check for lanthanides or actinides placeholder
        if (electronNumber === 'lanthanides' || electronNumber === 'actinides') {
            return;
        }
        // Check for boundary conditions and display an error message if out of range
        if (electronNumber < 1 || electronNumber > 118) {
            $('#popup-content').html('<p>Invalid element number. Boundary reached</p><p> <a href="/">Press here to go back to homepage</a></p>');
            $('.popup').addClass('active');
            return;
        }
        // AJAX request to get element details
        $.ajax({
            url: '/' + electronNumber,
            type: 'GET',
            success: function(response) {
                if (response.error) {
                    // Display error message if element not found
                    $('#popup-content').html('<p>' + response.error + ' <a href="/">Press here to go back to homepage</a></p>');
                } else {
                    // Display element details
                    var content = '<h2>' + response.name + ' (' + response.symbol + ')</h2>';
                    content += '<p>Atomic number: ' + response.electron + '</p>';
                    content += '<p>Atomic mass: ' + response.atomicmass + '<p>';
                    content += '<p>Electronegativity: ' + response.enegativity + '</p>';
                    content += '<p>Melting Point: ' + response.meltingpoint + '°K</p>';
                    content += '<p>Boiling Point: ' + response.boilingpoint + '°K</p>';
                    content += '<p>Year of Discovery: ' + response.ydiscover + '</p>';
                    content += '<p>Electron Configuration: ' + response.configuration + '</p>';
                    content += '<p>Group: ' + response.group + '</p>';
                    content += '<p>Period: ' + response.period + '</p>';
                    if (response.category) {
                        content += '<p>Category: ' + response.category + '</p>';
                    }
                    if (response.details){
                        content += '<p><a href="' + response.details + '" target="_blank">Click to view more details</a></p>';
                    }
                    $('#popup-content').html(content); // Insert content into popup
                }
                $('.popup').addClass('active');
            },
            error: function(error) {
                // Display error message if AJAX request fails
                $('#popup-content').html('<p>Error fetching element details. <a href="/">Press here to go back to homepage</a></p>');
                $('.popup').addClass('active');
            }
        });
    });
    // Event handler to close the popup
    $('.popup .close-btn').click(function() {
        $('.popup').removeClass('active'); // Hide the popup
    });
});
