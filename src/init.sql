PRAGMA foreign_keys = ON;

CREATE TABLE Drink (
    name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE PurchaseOrder (
                               -- replace with unixepoch('subsec') when sqlite3
                               -- version >= 3.38
    time REAL NOT NULL DEFAULT((julianday('now') - 2440587.5)*86400.0) PRIMARY KEY,
    drink_name TEXT NOT NULL,
    FOREIGN KEY (drink_name)
        REFERENCES Drink(name)
);
