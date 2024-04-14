const drink_grid = document.getElementById('drink-grid');
const buttons = drink_grid.getElementsByTagName('button');
for (const button of buttons) {
    button.onclick = function (e) {
        e.preventDefault();
        fetch('/api/submit_order', {
            method: 'POST',
            body: JSON.stringify({'order': button.value, 'event': Number(getEventId())})
        });
    }
}

function getEventId() {
    const inputs = document.getElementsByTagName('input');
    const eventInput = inputs.namedItem('event');
    return eventInput.value;
}
