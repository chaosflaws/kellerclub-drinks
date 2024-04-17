export default (eventId: string, drinks: Map<string, string>, target: HTMLElement | null) => {
    return {
        get localStorage() {
            const value = window.localStorage.getItem(keyFor(eventId));
            return value ? value.split(',') : [];
        },

        set localStorage(orders) {
            window.localStorage.setItem(keyFor(eventId), orders.join(','));
        },

        clear: () => window.localStorage.removeItem(keyFor(eventId)),

        display: (name: string) => {
            const displayName = drinks.get(name);
            if (!displayName) throw Error(`Unknown drink internal name ${name}!`)

            const orderNode = document.createElement('li');
            orderNode.appendChild(document.createTextNode(displayName));
            target?.appendChild(orderNode);
        }
    }
}

function keyFor(eventId: string) {
    return `event-${eventId}-orders`;
}
