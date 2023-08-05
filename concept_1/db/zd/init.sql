CREATE TABLE Payments (
    id SERIAL PRIMARY KEY,
    amount MONEY NOT NULL,
    payment_date DATE NOT NULL,
    iban TEXT NOT NULL
);

