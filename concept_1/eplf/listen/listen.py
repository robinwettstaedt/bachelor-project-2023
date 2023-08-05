"""
This script is run inside the EPLF-listen container.

It listens for messages on the 'validation' queue and iterates through the data it receives through said queue.

For each record in the message, it updates the corresponding entry in the 'Log' table to have the 'validated' field set to True
and the `faulty` field set to True if the IBAN is invalid.
"""


import json
from datetime import datetime
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


def update_db(data, cursor):
    type_of_data = data["type"]
    data = data["data"]

    # check the received dictionary for the type of data
    if type_of_data == "successful_insertion":

        # Iterate over the data
        for row in data:
            # Get the payment_id from the row
            payment_id = row[0]

            # Update the validated field in the 'Log' table where the payment_id matches
            cursor.execute(
                "UPDATE Log SET validated = True WHERE payment_id = %s",
                (payment_id,)
            )

    elif type_of_data == "invalid_iban":

        # Iterate over the data
        for row in data:
            # Get the payment_id from the row
            payment_id = row[0]

            # update all the rows with invalid IBANs
            cursor.execute(
                "UPDATE Log SET faulty = True WHERE payment_id = %s",
                (payment_id,)
            )


    print(f"Updated {len(data)} records in the 'Log' table of the EPLF database to be validated or faulty. \n")



# ------------- Message Queue functions ------------- #

def on_receive_message(ch, method, properties, body):
    # Decode the JSON string back into a Python list
    data = json.loads(body)

    # Connect to the database
    conn = connect_to_db(host='192.168.0.23', dbname='db', user='postgres', password='postgres')

    if conn:
        # Create a cursor from the connection
        cursor = conn.cursor()

        # Update the Log table in the database
        update_db(data, cursor)

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()

        # Acknowledge message so it can be removed from the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Message acknowledged: {method.delivery_tag}")



# ------------- Main function ------------- #

def main():
    # Provide authentication for the mq
    credentials = pika.PlainCredentials('rabbit', 'rabbit')

    # Creating the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.22', credentials=credentials, heartbeat=65535))
    channel = connection.channel()

    # Declare the queue from which to receive messages
    channel.queue_declare(queue='validation')

    # Declare the callback function
    channel.basic_consume(queue='validation', on_message_callback=on_receive_message, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')

    try:
        # Start the consumer in an infinite loop
        channel.start_consuming()
    except KeyboardInterrupt:
        # CTRL+C breaks the infinite loop and closes the connection
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    main()