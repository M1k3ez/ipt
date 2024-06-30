document.addEventListener('DOMContentLoaded', function () {
    const elements = document.querySelectorAll('.element');
    elements.forEach(element => {
        element.addEventListener('click', function () {
            const electron = this.getAttribute('data-electron');
            fetch(`/element/${electron}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(`Error fetching details for element ${electron}: ${data.error}`);
                        alert(data.error);
                    } else {
                        document.getElementById('element-title').innerText = `${data.name} (${data.symbol})`;
                        document.getElementById('element-details').innerText = data.details;
                        document.getElementById('element-enegativity').innerText = `Electronegativity: ${data.enegativity}`;
                        document.getElementById('element-meltingpoint').innerText = `Melting Point: ${data.meltingpoint} K`;
                        document.getElementById('element-boilingpoint').innerText = `Boiling Point: ${data.boilingpoint} K`;
                        document.getElementById('element-ydiscover').innerText = `Year of Discovery: ${data.ydiscover}`;
                        document.getElementById('element-modal').style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error(`Error fetching details for element ${electron}:`, error);
                });
        });
    });
    const modal = document.getElementById('element-modal');
    const span = document.getElementsByClassName('close')[0];
    span.onclick = function () {
        modal.style.display = 'none';
    }
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});
