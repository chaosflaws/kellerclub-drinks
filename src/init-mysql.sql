-- MySQL does not support:
-- - inline foreign key statements (... REFERENCES ...)
-- - deferred foreign key constraints

CREATE TABLE Drink (
    name VARCHAR(100) NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE Event (
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    end_time TIMESTAMP,
    name TEXT
);

CREATE TABLE PurchaseOrder (
    time TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP PRIMARY KEY,
    drink_name VARCHAR(100) NOT NULL,
    /*event TIMESTAMP NOT NULL,*/

    FOREIGN KEY (drink_name) REFERENCES Drink(name)
    /*FOREIGN KEY (event) REFERENCES Event(start_time)*/
);

CREATE TABLE SelectorLayout (
    name VARCHAR(100) NOT NULL PRIMARY KEY
);

CREATE TABLE SelectorButton (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    layout_name VARCHAR(100) NOT NULL,
    xpos INTEGER NOT NULL,
    ypos INTEGER NOT NULL,
    display_name TEXT,

    FOREIGN KEY (layout_name) REFERENCES SelectorLayout(name)
);

CREATE TABLE OrderButton (
    button_id INTEGER NOT NULL,
    drink_name VARCHAR(100) NOT NULL,

    FOREIGN KEY (button_id) REFERENCES SelectorButton(id),
    FOREIGN KEY (drink_name) REFERENCES Drink(name)
);

CREATE TABLE LinkButton (
    button_id INTEGER NOT NULL,
    linked_layout VARCHAR(100) NOT NULL,

    FOREIGN KEY (button_id) REFERENCES SelectorButton(id),
    FOREIGN KEY (linked_layout) REFERENCES SelectorLayout(name)
);
