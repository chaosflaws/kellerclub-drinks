import {Query} from "../view.js";
import {OrderList} from "./order_list.js";
import {data, drinkGrid, gridButtons} from "./drink_selector.js";

const orderList = Query(drinkGrid)
    .oneClass('order-list')
    .oneTag('ul')
    .value();

const submitButton = Query(drinkGrid)
    .oneClass('order-list')
    .oneTag('button')
    .value();

const orders = new OrderList(data.eventId, await data.drinks, orderList);

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
