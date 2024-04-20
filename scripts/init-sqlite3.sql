PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 10;

CREATE TABLE Drink (
    name TEXT NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL,
    base_price INTEGER NOT NULL -- oldest reported price
);

CREATE TABLE Prices (
    drink TEXT NOT NULL
        REFERENCES Drink(name),
    end_time NUMERIC NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE Event (
    start_time NUMERIC NOT NULL DEFAULT(unixepoch()) PRIMARY KEY,
    end_time INTEGER,
    name TEXT
);

CREATE TABLE PurchaseOrder (
    time NUMERIC NOT NULL DEFAULT(unixepoch('subsec')),
    drink_name TEXT NOT NULL
        REFERENCES Drink(name),
    event NUMERIC NOT NULL
        REFERENCES Event(start_time)
);

CREATE TABLE SelectorLayout (
    name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE SelectorButton (
    id INTEGER NOT NULL PRIMARY KEY,
    layout_name TEXT NOT NULL
        REFERENCES SelectorLayout(name),
    xpos INTEGER NOT NULL,
    ypos INTEGER NOT NULL,
    display_name TEXT
);

CREATE TABLE OrderButton (
    button_id INTEGER NOT NULL
        REFERENCES SelectorButton(id),
    drink_name TEXT NOT NULL
        REFERENCES Drink(name)
);

CREATE TABLE LinkButton (
    button_id INTEGER NOT NULL
        REFERENCES SelectorButton(id),
    linked_layout TEXT NOT NULL
        REFERENCES SelectorLayout(name)
);
