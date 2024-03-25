PRAGMA foreign_keys = ON;

CREATE TABLE Drink (
    name TEXT NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE Event (
    start_time INTEGER NOT NULL DEFAULT(unixepoch()) PRIMARY KEY,
    end_time INTEGER,
    name TEXT
);

CREATE TABLE PurchaseOrder (
    time REAL NOT NULL DEFAULT(unixepoch('subsec')) PRIMARY KEY,
    drink_name TEXT NOT NULL
        REFERENCES Drink(name)
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
