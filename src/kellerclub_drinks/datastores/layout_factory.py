from collections import defaultdict
from typing import Optional

from ..model.layouts import Button, OrderButton, LinkButton, Layout

OrderRow = tuple[
    str,  # layout_name
    int,  # xpos
    int,  # ypos
    str,  # display_name
    str]  # drink_name

LinkRow = tuple[
    str,  # layout_name
    int,  # xpos
    int,  # ypos
    str,  # display_name
    str]  # linked_layout

ButtonGrid = list[list[Optional[Button]]]


def from_button_rows(order_rows: list[OrderRow],
                     link_rows: list[LinkRow]) -> dict[str, Layout]:

    buttons_to_layouts: dict[str, ButtonGrid]
    buttons_to_layouts = defaultdict(lambda: _empty_grid(5, 5))

    for row in order_rows:
        layout_name, xpos, ypos, display_name, drink_name = row
        buttons_to_layouts[layout_name][xpos][ypos] = OrderButton(display_name, drink_name)

    for row in link_rows:
        layout_name, xpos, ypos, display_name, linked_layout = row
        buttons_to_layouts[layout_name][xpos][ypos] = LinkButton(display_name, linked_layout)

    layouts = {k: Layout(k, v) for k, v in buttons_to_layouts.items()}
    for layout in layouts:
        for rows in layout:
            for button in rows:
                if isinstance(button, LinkButton):
                    setattr(button, 'layout', layouts[button.layout])

    return layouts


def _empty_grid(x: int, y: int) -> ButtonGrid:
    result: ButtonGrid = []
    for _ in range(y):
        result.append([None] * x)
    return result
