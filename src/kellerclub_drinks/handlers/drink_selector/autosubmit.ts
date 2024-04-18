import {InvisibleOrderList} from "./order_list.js";
import {data, gridButtons} from "./drink_selector.js";

const orders = new InvisibleOrderList(data.eventId);
void orders.submit();

for (const button of gridButtons) {
    button.addEventListener('click', e => {
        e.preventDefault();
        orders.add(button.value);
        void orders.submit();
    });
}
