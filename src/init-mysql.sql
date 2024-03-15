CREATE TABLE Drink (
    name VARCHAR(100) NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE PurchaseOrder (
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    drink_name VARCHAR(100) NOT NULL
        REFERENCES Drink(name)
);

CREATE TABLE SelectorLayout (
    name VARCHAR(100) NOT NULL PRIMARY KEY
);

CREATE TABLE SelectorButton (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    layout_name VARCHAR(100) NOT NULL
        REFERENCES SelectorLayout(name),
    xpos INTEGER NOT NULL,
    ypos INTEGER NOT NULL,
    display_name TEXT
);

CREATE TABLE OrderButton (
    button_id INTEGER NOT NULL
        REFERENCES SelectorButton(id),
    drink_name VARCHAR(100) NOT NULL
        REFERENCES Drink(name)
);

CREATE TABLE LinkButton (
    button_id INTEGER NOT NULL
        REFERENCES SelectorButton(id),
    linked_layout VARCHAR(100) NOT NULL
        REFERENCES SelectorLayout(name)
);
