"""
This script will fill the 'Payments' table of the EPLF database with 30,000 rows of randomly generated payment data.

Each row has a 0.2% chance of containing an entry with an invalid IBAN.
"""

import random
import datetime
from faker import Faker
import psycopg2


# Capture the start time
start_time = datetime.datetime.now()

# Setup Faker
# set it the german locale for german IBANs
fake = Faker('de_DE')

# Connect to your postgres DB
conn = psycopg2.connect(
    dbname="db",
    user="postgres",
    password="postgres",
    host="192.168.0.23"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# This script assumes that the Payments table schema is (id serial primary key, amount money, iban text, payment_date date)
for i in range(30000):  # Generate 500,000 rows
    amount = round(random.uniform(1, 1000), 2)  # Random amount between 1 and 1000 with 2 decimal places
    payment_date = fake.date_between(start_date='-1y', end_date='today')  # Random date within last year

    # Generate a random IBAN
    iban = fake.iban()

    # Make an IBAN invalid with a 0.2% chance
    should_be_invalid = random.choices(
        population=[True, False],
        weights=[0.001, 0.999],  # 0.1% chance of True, 99.9% chance of False
        k=1
    )[0]

    if should_be_invalid:
        iban = iban[:-2] + '00'  # Replace last two digits with "00"

    # Execute insert statement
    cur.execute(
        "INSERT INTO Payments (amount, iban, payment_date) VALUES (%s::money, %s, %s)",
        (str(amount), iban, payment_date)
    )

    print(f"Inserted row {i + 1}")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

# Capture the end time
end_time = datetime.datetime.now()

# Calculate the difference between end and start times
delta = end_time - start_time

# Print the elapsed time
print(f"Time taken to run the script: {delta}")