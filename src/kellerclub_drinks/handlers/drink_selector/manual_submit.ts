import {Query} from "../view.js";
import {OrderList} from "./order_list.js";
import {data, drinkGrid, gridButtons} from "./drink_selector.js";

const orderListQuery = Query(drinkGrid)
    .oneClass('order-list');

const orderListContent = orderListQuery
    .oneTag('ul')
    .value();

const sum = orderListQuery
    .oneClass('sum')
    .value();

const submitButton = orderListQuery
    .someTags('button')
    .withClass('submit')
    .value();

const resetButton = orderListQuery
    .someTags('button')
    .withClass('reset')
    .value();

const orders = new OrderList(data.eventId, data.drinks, orderListContent, sum);
const initComplete = orders.init();

resetButton.classList.add('hidden');
void initComplete.then(() => {
    const initialItems = orderListItems(orderListQuery);
    initDeleteButtons(initialItems);
});

for (const button of gridButtons) {
    button.addEventListener('click', e => {
        e.preventDefault();
        void orders.add(button.value).then(() => {
            const entries = orderListItems(orderListQuery);
            const newEntry = entries[entries.length-1];
            initDeleteButtons([newEntry]);
        });
    });
}
submitButton.addEventListener('click', e => {
    e.preventDefault();
    void orders.submit();
});

function initDeleteButtons(entries: HTMLElement[]) {
    const deleteButtons = Query(entries)
        .oneClass('bi-trash')
        .value();
    for (const button of deleteButtons) {
        button.classList.remove('hidden');
        const value = Query(button).parent().oneTag('input').value().value;
        button.addEventListener('click', e => {
            e.preventDefault();
            orders.remove(value);
        })
    }
}

function orderListItems(parent: Query<Element>) {
    return parent
        .oneTag('ul')
        .anyTags('li')
        .value();
}
