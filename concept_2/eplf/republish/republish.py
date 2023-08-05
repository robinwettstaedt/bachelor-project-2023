"""
This script is run inside the EPLF-republish container.

It retrieves all the unvalidated rows from the 'Log' table of the EPLF database,
filters out the rows that have been inserted less than 20 minutes ago,
as well as the ones that are faulty (previously found to have invalid IBANs).

It then publishes the filtered data to the RabbitMQ 'data' queue to be consumed by the ZD once more.

It runs in a loop with a 10 minute delay between each iteration.
"""


import json
import time
import datetime
import pika
import psycopg2



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


def get_data_from_log(conn):
    # This function retrieves all the unvalidated rows from the 'Log' table
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM Log
        WHERE validated = false
    """)

    return cursor.fetchall()


def filter_log_data(data) -> list:
    # This function filters out the rows that have been inserted less than 20 minutes ago
    filtered_data = []

    for row in data:
        payment_id = row[0]
        iban = row[1]
        validated = row[2]
        inserted = row[3]

        # calculate the time difference between now and the time the row was inserted
        time_diff = (datetime.datetime.utcnow() - inserted).total_seconds()

        # if the time difference is greater than 2 minutes, add the row to the filtered data
        if time_diff > 120:
            filtered_data.append((payment_id, iban, validated, inserted))

    return filtered_data


def get_data_from_payments(conn, log_data):
    cursor = conn.cursor()

    # If log_data is empty, return an empty list
    if not log_data:
        return []


    if len(log_data) == 1:
        # If there's only one row, doing the standard way will result in a syntax error within the SQL query
        id = log_data[0][0]

        cursor.execute(f"""
                        SELECT id, amount, iban, TO_CHAR(payment_date,'YYYY-MM-DD') as payment_date
                        FROM Payments
                        WHERE id = {id}
                    """)

    else:
        # Build the tuple of ids
        ids = tuple(row[0] for row in log_data)


        cursor.execute(f"""
                        SELECT id, amount, iban, TO_CHAR(payment_date,'YYYY-MM-DD') as payment_date
                        FROM Payments
                        WHERE id IN {ids}
                    """)

    return cursor.fetchall()



# ------------- Main function ------------- #

def main():
    # Connect to database.
    conn = connect_to_db(host='192.168.0.23', dbname='db', user='postgres', password='postgres')

    # Provide authentication for the mq
    credentials = pika.PlainCredentials('rabbit', 'rabbit')

    # Creating the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.22', credentials=credentials, heartbeat=65535))
    channel = connection.channel()

    # Declare the queue from which to receive messages
    channel.queue_declare(queue='data')

    sent_counter = 0

    while True:
        # Retrieve data from the database
        log_data = get_data_from_log(conn)

        print(f"Retrieved {len(log_data)} rows from the 'Log' table.")

        # Filter out the rows that have been inserted less than 20 minutes ago
        filtered_data = filter_log_data(log_data)

        print(f"Found {len(filtered_data)} rows that are old enough to be resent.")

        # Retrieve up to 1000 rows from the 'Payments' table that correspond to the filtered data
        payments_data = get_data_from_payments(conn, filtered_data)

        print(f"Retrieved {len(payments_data)} rows from the 'Payments' table.")

        # Only publish a message if rows to resend have been found
        if len(payments_data) > 0:

            # Convert all data to a JSON string and send as a single message
            message = json.dumps(payments_data)

            # Publish the message to the queue
            channel.basic_publish(exchange='', routing_key='data', body=message)

            # Increment the counter
            sent_counter += len(payments_data)
            print(f"Sent {sent_counter} rows in total \n")

        # Wait 1 minute before sending the next message
        time.sleep(60)


if __name__ == '__main__':
    main()
