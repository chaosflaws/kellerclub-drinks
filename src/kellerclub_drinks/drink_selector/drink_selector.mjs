const drink_grid = document.getElementById('drink-grid');
const buttons = drink_grid.getElementsByTagName('button');
for (const button of buttons) {
    button.onclick = function (e) {
        e.preventDefault();
        fetch('add_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: button.name + '=' + button.value
        });
    }
}
