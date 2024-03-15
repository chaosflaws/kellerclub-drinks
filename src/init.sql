PRAGMA foreign_keys = ON;

CREATE TABLE Drink (
    name TEXT NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE PurchaseOrder (
                               -- replace with unixepoch('subsec') when sqlite3
                               -- version >= 3.38
    time REAL NOT NULL DEFAULT((julianday('now') - 2440587.5)*86400.0) PRIMARY KEY,
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
    display_name TEXT NOT NULL
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
