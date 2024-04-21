import {Query} from "../view.js";
import {OrderList} from "./order_list.js";
import {data, drinkGrid, gridButtons} from "./drink_selector.js";

const orderList = Query(drinkGrid)
    .oneClass('order-list')
    .oneTag('ul')
    .value();

const sum = Query(drinkGrid)
    .oneClass('order-list')
    .oneClass('sum')
    .value();

const submitButton = Query(drinkGrid)
    .oneClass('order-list')
    .someTags('button')
    .withClass('submit')
    .value();

const resetButton = Query(drinkGrid)
    .oneClass('order-list')
    .someTags('button')
    .withClass('reset')
    .value();

const orders = new OrderList(data.eventId, data.drinks, orderList, sum);
orders.init();

resetButton.classList.add('hidden');

for (const button of gridButtons) {
    button.addEventListener('click', e => {
        e.preventDefault();
        orders.add(button.value);
    });
}
submitButton.addEventListener('click', e => {
    e.preventDefault();
    void orders.submit();
});
