export default (eventId, drinks) => {
    return {
        get localStorage() {
            return window.localStorage[eventId]
                ? window.localStorage[eventId].split(',')
                : [];
        },

        set localStorage(orders) {
            window.localStorage[eventId] = orders.join(',');
        },

        display: (orderList, name) => {
            const displayName = drinks.get(name);
            const orderNode = document.createElement('li');
            orderNode.appendChild(document.createTextNode(displayName));
            orderList.appendChild(orderNode);
        }
    }
}
