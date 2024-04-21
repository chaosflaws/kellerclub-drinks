import {Query} from "../view.js";

type Drink = [string, number];

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
        else {
            orders.splice(index, 1);
            this.storage = orders;
        }
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
    readonly #container: Element;
    readonly #sum: Element;
    readonly #drinks: Promise<Map<string, Drink>>;

    constructor(eventId: number, drinks: Promise<Map<string, Drink>>,
                container: Element, sum: Element) {
        super(eventId);
        this.#container = container;
        this.#sum = sum;
        this.#drinks = drinks;
    }

    /**
     * Displays the orders in local storage in the target.
     */
    async init() {
        await this.#drinks;
        this.#hideAll();
        for (const order of this.storage) {
            void this.#show(order);
        }
        void this.#updateSum();
    }

    /**
     * Adds an order to local storage and displays it.
     */
    async add(order: string) {
        super.add(order);
        await this.#show(order);
        return this.#updateSum();
    }

    /**
     * Removes an order from local storage and removes it from the target
     * container.
     */
    remove(order: string) {
        super.remove(order);
        this.#hide(order);
        void this.#updateSum();
    }

    /**
     * Submits orders in local storage and clears the container.
     */
    async submit() {
        if (this.storage.length) {
            await super.submit();
            this.#hideAll();
            void this.#updateSum();
        }
    }

    async #show(name: string) {
        const drink = (await this.#drinks).get(name);
        if (!drink) throw Error(`Unknown drink internal name ${name}!`)

        const displayName = drink[0];
        const price = drink[1];

        const orderNode = this.#createOrderElement(name, displayName, price);
        this.#container.appendChild(orderNode);
    }

    #createOrderElement(name: string, displayName: string, price: number) {
        const template = Query()
            .someTags('template')
            .withId('order-list-child')
            .value();
        const clone = template.content.cloneNode(true) as DocumentFragment;
        const root = Query(clone);
        root.oneTag('li').value().dataset.orderName = name;
        root.oneClass('name').value().textContent = displayName;
        root.oneClass('price').value().textContent = this.#euro(price);
        root.oneTag('input').value().defaultValue = name;
        return clone;
    }

    #hide(name: string) {
        const candidates = this.#container.querySelectorAll(`[data-order-name="${name}"]`);
        if (!candidates.length) throw Error(`Should hide order ${name}, but not found!`);

        candidates[0].remove();

        void this.#updateSum();
    }

    #hideAll() {
        this.#container.replaceChildren();
    }

    async #updateSum() {
        const drinks = await this.#drinks;
        const price = this.storage
            .map(order => drinks.get(order)?.[1] ?? 0)
            .reduce((x, y) => x + y, 0);
        this.#sum.textContent = this.#euro(price);
    }

    #euro(price: number) {
        const euros = String(Math.trunc(price / 100));
        const cents = String(price % 100).padStart(2, '0');
        return `${euros},${cents} €`;
    }
}
