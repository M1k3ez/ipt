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
                    content += '<p>Electron: ' + response.electron + '</p>';
                    content += '<p>Electro negativity: ' + response.enegativity + '</p>';
                    content += '<p>Melting Point: ' + response.meltingpoint + '°C</p>';
                    content += '<p>Boiling Point: ' + response.boilingpoint + '°C</p>';
                    content += '<p>Details: ' + response.details + '</p>';
                    content += '<p>Year of Discovery: ' + response.ydiscover + '</p>';
                    $('#popup-content').html(content);
                }
                $('#popup').show();
            },
            error: function(error) {
                $('#popup-content').html('<p>Error fetching element details.</p>');
                $('#popup').show();
            }
        });
    });

    $('#popup-close').click(function() {
        $('#popup').hide();
    });
});
