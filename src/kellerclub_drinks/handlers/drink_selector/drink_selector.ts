import orders from './order_list.js';

const drinkGrid = document.getElementById('drink-grid');
if (!drinkGrid) throw Error('No drink grid element found!');

const orderList = document.getElementById('order-list');

const buttons = drinkGrid
    .getElementsByClassName('grid')[0]
    .getElementsByTagName('button');

const drinks = fetch('/api/drinks')
    .then(response => response.json(), () => Error('Could not fetch drinks!'))
    .then(json => new Map(Object.entries(json)) as Map<string, string>);

const eventId = getEventId(drinkGrid);
const eventOrders = orders(eventId, await drinks, orderList);

if (drinkGrid.dataset.autosubmit === 'true') {
    for (const button of buttons) {
        button.addEventListener('click', submitOrder);
    }
} else if (drinkGrid.dataset.autosubmit === 'false') {
    for (const button of buttons) {
        button.addEventListener('click', addOrder);
    }
} else {
    throw Error('Parameter "autosubmit" is neither "true" nor "false"!');
}

if (drinkGrid.dataset.autosubmit === 'true') {
    if (eventOrders.localStorage.length) {
        fetch('/api/submit_order', {
            method: 'POST',
            body: JSON.stringify({'orders': eventOrders.localStorage, 'event': eventId})
        });
    }
    eventOrders.clear();
} else {
    displayStoredOrders();
}

function getEventId(drinkGrid: HTMLElement) {
    const inputs = drinkGrid.getElementsByTagName('input');
    const eventInput = inputs.namedItem('event');
    if (!eventInput) throw Error('Hidden input with event ID not found!');

    return Number(eventInput.value);
}

function submitOrder(this: HTMLButtonElement, e: Event) {
    e.preventDefault();
    fetch('/api/submit_order', {
        method: 'POST',
        body: JSON.stringify({'orders': [this.value], 'event': eventId})
    });
}

async function addOrder(this: HTMLButtonElement, e: Event) {
    e.preventDefault();
    eventOrders.localStorage = [...eventOrders.localStorage, this.value];
    eventOrders.display(this.value);
}

function displayStoredOrders() {
    for (const order of eventOrders.localStorage) {
        eventOrders.display(order);
    }
}
