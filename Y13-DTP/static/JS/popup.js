$(document).ready(function() {
    $('.element-link').click(function(event) {
        event.preventDefault();
        var electronNumber = $(this).data('id');
        
        // Ignore placeholders
        if (electronNumber === 'lanthanides' || electronNumber === 'actinides') {
            return;
        }
        
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
                    content += '<p>Melting Point: ' + response.meltingpoint + '°K</p>';
                    content += '<p>Boiling Point: ' + response.boilingpoint + '°K</p>';
                    content += '<p>Year of Discovery: ' + response.ydiscover + '</p>';
                    content += '<p>Electron Configuration: ' + response.configuration + '</p>';
                    content += '<p>Group: ' + response.group + '</p>';
                    content += '<p>Period: ' + response.period + '</p>';
                    if (response.category) {
                        content += '<p>Category: ' + response.category + '</p>';
                    }
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
