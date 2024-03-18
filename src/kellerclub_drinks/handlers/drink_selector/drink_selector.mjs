const drink_grid = document.getElementById('drink-grid');
const buttons = drink_grid.getElementsByTagName('button');
for (const button of buttons) {
    button.onclick = function (e) {
        e.preventDefault();
        fetch('/api/add_order', {
            method: 'POST',
            body: JSON.stringify({'order': button.value})
        });
    }
}
