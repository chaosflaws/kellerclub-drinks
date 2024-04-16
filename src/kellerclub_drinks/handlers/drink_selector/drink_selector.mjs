import orders from './order_list.mjs';

const drinkGrid = document.getElementById('drink-grid');
const orderList = document.getElementById('order-list');
const buttons = drinkGrid.getElementsByTagName('button');

const drinks = fetch('/api/drinks')
    .then(response => response.json(), () => Error('Could not fetch drinks!'))
    .then(json => new Map(Object.entries(json)));

const eventId = getEventId();
const eventOrders = orders(eventId, await drinks);

if (drinkGrid.dataset.autosubmit === 'true') {
    for (const button of buttons) {
        button.onclick = submitOrder;
    }
} else if (drinkGrid.dataset.autosubmit === 'false') {
    for (const button of buttons) {
        button.onclick = addOrder;
    }
} else {
    Error('Parameter "autosubmit" is neither "true" nor "false"!');
}

displayStoredOrders();

function getEventId() {
    const inputs = drinkGrid.getElementsByTagName('input');
    const eventInput = inputs.namedItem('event');
    return Number(eventInput.value);
}

function submitOrder(e) {
    e.preventDefault();
    fetch('/api/submit_order', {
        method: 'POST',
        body: JSON.stringify({'order': this.value, 'event': eventId})
    });
}

async function addOrder(e) {
    e.preventDefault();
    eventOrders.localStorage = [...eventOrders.localStorage, this.value];
    eventOrders.display(orderList, this.value);
}

function displayStoredOrders() {
    for (const order of eventOrders.localStorage) {
        eventOrders.display(orderList, order);
    }
}
