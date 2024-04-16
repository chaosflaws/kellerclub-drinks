export default (eventId, drinks) => {
    return {
        get localStorage() {
            return window.localStorage.getItem(keyFor(eventId))
                ? window.localStorage.getItem(keyFor(eventId)).split(',')
                : [];
        },

        set localStorage(orders) {
            window.localStorage.setItem(keyFor(eventId), orders.join(','));
        },

        clear: () => window.localStorage.removeItem(keyFor(eventId)),

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
