"""
This script listens to the 'data' queue and processes the incoming messages containing payment data.

The insertion has a random delay between 10ms and 100ms to simulate a real-world scenario.

After validating the IBANs, it inserts the received data into the 'Payments' table of the ZD database.

Each row is also inserted into the either the 'Log' table or the `InvalidLog` table of the ZD database, based on the validity of its IBAN.

There is also a 0.01% chance that the insertion is skipped to simulate a system error.

This will result in the row not being added to either of the 'Log' or 'InvalidLog' tables and it getting noticed later by the validation service. 
"""


import json
import time
import random
from datetime import datetime
import pika
import psycopg2
import psycopg2.errors
from schwifty import IBAN
from schwifty.exceptions import InvalidChecksumDigits



# ------------- Database / data functions ------------- #

def connect_to_db(host, dbname, user, password, port=5432):
    conn = None
    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port,
        )
        print(f"Successfully connected to PostgreSQL database with id {id(conn)}")
    except Exception as e:
        print(f"Error occurred: {e}")
    return conn


def is_iban_valid(iban):
    # Returns True if the IBAN is valid, False otherwise
    try:
        iban = IBAN(iban)
        return True
    except InvalidChecksumDigits:
        return False


def insert_into_payments(conn, data):
    successfully_inserted_data = []
    invalid_iban_data = []
    system_error_counter = 0
    received_invalid_data_counter = 0
    received_duplicate_data_counter = 0

    # Create a database cursor
    cursor = conn.cursor()

    def generate_sleep_time():
        # This function generates a random sleep time in seconds,
        # primarily between 0.005 and 0.025 seconds (5 to 25 milliseconds) with a 95% probability,
        # or 0.05 seconds (50 milliseconds) with a 5% probability.\

        return random.choices(
            population=[random.uniform(0.005, 0.025), 0.05],  # The possible sleep times
            weights=[0.95, 0.05],  # The probabilities for each sleep time
            k=1
        )[0]

    # Check if data is list or single record
    if isinstance(data, list):
        # Loop through each record in list
        for item in data:

            # Validate the data item
            if len(item) < 4:
                print(f"Received invalid data: {item}")
                received_invalid_data_counter += 1
                continue

            # Validate the IBAN
            if not is_iban_valid(item[2]):
                invalid_iban_data.append(item)
                continue

            try:
                # delay for a random duration
                time.sleep(generate_sleep_time())

                # Random 0.1% chance to skip insertion (simulating an internal error)
                if random.random() < 0.001:
                    system_error_counter += 1
                    continue

                # Insert the record into database
                cursor.execute("INSERT INTO Payments (id, amount, iban, payment_date) VALUES (%s, %s, %s, %s)", (item[0], item[1], item[2], item[3]))
                conn.commit()

                # Add the record to the list of successfully inserted records
                successfully_inserted_data.append(item)

            except psycopg2.errors.UniqueViolation:
                # Duplicate entry / idempotency
                received_duplicate_data_counter += 1
                conn.rollback()


    else:
        # Validate the data item
        if len(data) < 4:
            received_invalid_data_counter += 1
            return successfully_inserted_data, invalid_iban_data

        # Validate the IBAN
        if not is_iban_valid(data[2]):
            invalid_iban_data.append(data)
            return successfully_inserted_data, invalid_iban_data

        # Insert single record into database
        try:
            # delay for a random duration
            time.sleep(generate_sleep_time())

            # Random 0.1% chance to skip insertion (simulating an internal error)
            if random.random() < 0.001:
                system_error_counter += 1
                return successfully_inserted_data, invalid_iban_data

            cursor.execute("INSERT INTO Payments (id, amount, iban, payment_date) VALUES (%s, %s, %s, %s)", (data[0], data[1], data[2], data[3]))
            conn.commit()

        # Duplicate entry / idempotency
        except psycopg2.errors.UniqueViolation:
            # Ignore duplicate entry
            received_duplicate_data_counter += 1
            conn.rollback()

    # Print status
    if isinstance(data, list):
        print(f"Successfully inserted {len(successfully_inserted_data)} out of the {len(data)} records received into the 'Payments' table of the ZD database.")
        print(f"Invalid IBANs: {len(invalid_iban_data)}")
        print(f"System errors: {system_error_counter}")
        print(f"Invalid data: {received_invalid_data_counter}")
        print(f"Duplicate data: {received_duplicate_data_counter}")
    else:
        print(f"Successfully inserted the only received record with id {data[0]} into the 'Payments' table of the ZD database.")
        print(f"Invalid IBANs: {len(invalid_iban_data)}")
        print(f"System errors: {system_error_counter}")
        print(f"Invalid data: {received_invalid_data_counter}")
        print(f"Duplicate data: {received_duplicate_data_counter}")

    return successfully_inserted_data, invalid_iban_data


def insert_into_log_db(conn, successfully_inserted_data, invalid_iban_data):
    # Create a database cursor
    cursor = conn.cursor()

    # Insert the successfully inserted data into the 'Log' table of the ZD database
    for item in successfully_inserted_data:

        cursor.execute(
            """
            INSERT INTO Log (payment_id, iban, validated, inserted)
            SELECT %s, %s, False, now() AT TIME ZONE 'UTC'
            WHERE NOT EXISTS (
                SELECT 1 FROM Log WHERE payment_id = %s
            )
            """,
            (item[0], item[2], item[0])
        )

        conn.commit()

    print(f"Successfully inserted {len(successfully_inserted_data)} valid rows into the 'Log' table of the ZD database.")

    # Insert the invalid IBAN data into the 'Log' table of the ZD database
    for item in invalid_iban_data:

        cursor.execute(
            """
            INSERT INTO InvalidLog (payment_id, iban, validated, inserted)
            SELECT %s, %s, False, now() AT TIME ZONE 'UTC'
            WHERE NOT EXISTS (
                SELECT 1 FROM InvalidLog WHERE payment_id = %s
            )
            """,
            (item[0], item[2], item[0])
        )

        conn.commit()


    print(f"Successfully inserted {len(invalid_iban_data)} rows with invalid IBANs into the 'InvalidLog' table of the ZD database.")



# ------------- Message Queue functions ------------- #

def on_receive_message(ch, method, properties, body):
    data = json.loads(body)

    print(f"\nReceived message with {len(data)} rows.")

    # Connect to the DB
    conn = connect_to_db(host='192.168.0.24', dbname='db', user='postgres', password='postgres')

    # Insert data into payments DB
    successfully_inserted_data, invalid_iban_data = insert_into_payments(conn, data)

    # Insert successfully inserted data into the 'Log' table of the ZD database
    if successfully_inserted_data or invalid_iban_data:
        insert_into_log_db(conn, successfully_inserted_data, invalid_iban_data)

    # Acknowledge message so it can be removed from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Message acknowledged: {method.delivery_tag}")

    # Close the database connection when done
    if conn:
        conn.close()



# ------------- Main function ------------- #

def main():
    # Provide authentication for the mq
    credentials = pika.PlainCredentials('rabbit', 'rabbit')

    # Creating the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.22', credentials=credentials, heartbeat=65535))
    channel = connection.channel()

  # Declare the queue from which to receive messages
    channel.queue_declare(queue='data')

    # Set 'on_receive_message' as the callback function for received messages
    channel.basic_consume(queue='data', on_message_callback=on_receive_message, auto_ack=False)

    # Print status
    print('Awaiting messages. To exit press CTRL+C')

    try:
        # Start consumer in infinite loop.
        channel.start_consuming()
    except KeyboardInterrupt:
        # Handle shutdown signal.
        channel.stop_consuming()
        connection.close()


if __name__ == '__main__':
    main()