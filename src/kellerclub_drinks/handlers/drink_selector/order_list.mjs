export default (eventId, drinks) => {
    return {
        get localStorage() {
            return window.localStorage[keyFor(eventId)]
                ? window.localStorage[keyFor(eventId)].split(',')
                : [];
        },

        set localStorage(orders) {
            window.localStorage[keyFor(eventId)] = orders.join(',');
        },

        display: (target, name) => {
            const displayName = drinks.get(name);
            const orderNode = document.createElement('li');
            orderNode.appendChild(document.createTextNode(displayName));
            target.appendChild(orderNode);
        }
    }
}

function keyFor(eventId) {
    return `event-${eventId}-orders`;
}
