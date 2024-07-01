$(document).ready(function() {
    $('.element-link').click(function(event) {
        event.preventDefault();
        var electronNumber = $(this).data('id');
        $.ajax({
            url: '/' + electronNumber,
            type: 'GET',
            success: function(response) {
                if (response.error) {
                    $('#popup-content').html('<p>' + response.error + '</p>');
                } else {
                    var content = '<h2>' + response.name + ' (' + response.symbol + ')</h2>';
                    content += '<p>Atomic number: ' + response.electron + '</p>';
                    content += '<p>Electronegativity: ' + response.enegativity + '</p>';
                    content += '<p>Melting Point: ' + response.meltingpoint + '°C</p>';
                    content += '<p>Boiling Point: ' + response.boilingpoint + '°C</p>';
                    content += '<p>Year of Discovery: ' + response.ydiscover + '</p>';
                    content += '<p>Electron Configuration: ' + response.configuration + '</p>';
                    $('#popup-content').html(content);
                }
                $('.popup').addClass('active');
            },
            error: function(error) {
                $('#popup-content').html('<p>Error fetching element details.</p>');
                $('.popup').addClass('active');
            }
        });
    });

    $('.popup .close-btn').click(function() {
        $('.popup').removeClass('active');
    });
});
