function submit(eventId: number, orders: string[]) {
    return fetch('/api/orders/submit', {
        method: 'POST',
        body: JSON.stringify({'orders': orders, 'event': eventId})
    });
}

export class InvisibleOrderList {
    readonly #eventId: number;
    readonly #key: string;

    constructor(eventId: number) {
        this.#eventId = eventId;
        this.#key = `event-${String(eventId)}-orders`;
    }

    /**
     * Adds an order to local storage.
     */
    add(order: string) {
        const orders = this.storage;
        orders.push(order);
        this.storage = orders;
    }

    /**
     * Removes an order from local storage.
     */
    remove(order: string) {
        const orders = this.storage;
        const index = orders.indexOf(order);

        if (index == -1) throw Error(`Order ${order} to be removed, but not found!`);
        else this.storage = orders.splice(index, 1);
    }

    /**
     * Submits all orders in local storage.
     */
    async submit() {
        if (this.storage.length) {
            await submit(this.#eventId, this.storage);
            this.storage = [];
        }
    }

    protected get storage() {
        const value = window.localStorage.getItem(this.#key);
        if (!value) return [];
        else return value.split(',');
    }

    protected set storage(value: string[]) {
        window.localStorage.setItem(this.#key, value.join(','));
    }
}

export class OrderList extends InvisibleOrderList {
    readonly #target: Element;
    readonly #drinks: Map<string, string>;

    constructor(eventId: number, drinks: Map<string, string>,
                target: Element) {
        super(eventId);
        this.#target = target;
        this.#drinks = drinks;
    }

    /**
     * Displays the orders in local storage in the target.
     */
    init() {
        for (const order of this.storage) {
            this.#show(order);
        }
    }

    /**
     * Adds an order to local storage and displays it.
     */
    add(order: string) {
        super.add(order);
        this.#show(order);
    }

    /**
     * Removes an order from local storage and removes it from the target
     * container.
     */
    remove(order: string) {
        super.remove(order);
        this.#hide(order);
    }

    /**
     * Submits orders in local storage and clears the container.
     */
    async submit() {
        if (this.storage.length) {
            await super.submit();
            this.#hideAll();
        }
    }

    #show(name: string) {
        const displayName = this.#drinks.get(name);
        if (!displayName) throw Error(`Unknown drink internal name ${name}!`)

        const orderNode = this.#createOrderElement(name, displayName);
        this.#target.appendChild(orderNode);
    }

    #createOrderElement(name: string, displayName: string) {
        const orderNode = document.createElement('li');
        orderNode.dataset.orderName = name;
        orderNode.appendChild(document.createTextNode(displayName));
        return orderNode;
    }

    #hide(name: string) {
        const candidates = this.#target.querySelectorAll(`[data-orderName="${name}"]`);
        if (!candidates.length) throw Error(`Should remove order ${name}, but not found!`);

        candidates[0].remove();
    }

    #hideAll() {
        this.#target.replaceChildren();
    }
}
