"""
This script is run in the zd-validation container.

It listens for messages from the validator via the message queue,
which can contain data or be empty.

The script will react the following way:

No data:
    - triggers it to fetch and send the unvalidated rows in the 'Log' table of the ZD DB back to the validator

Data:
    - contains the rows that were compared and validated by the validator service which are then updated in the 'Log' table of the ZD DB
"""


import json
import pika
import psycopg2
import psycopg2.errors



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
        print(f"\nSuccessfully connected to PostgreSQL database with id {id(conn)}")
    except Exception as e:
        print(f"Error occurred: {e}")
    return conn


def get_data_from_log(conn):
    # This function retrieves all the unvalidated rows from the 'Log' table
    cursor = conn.cursor()

    cursor.execute("""
        SELECT payment_id, validated, iban
        FROM Log
        WHERE validated = false
    """)

    return cursor.fetchall()



def update_log(conn, data):
    # update the corresponding rows in the 'Log' table of the ZD database to be validated
    cursor = conn.cursor()

    # Iterate over the data
    for row in data:
        # Get the payment_id from the row
        payment_id = row[0]

        # Update the validated field in the 'Log' table where the payment_id matches
        cursor.execute(
            "UPDATE Log SET validated = True WHERE payment_id = %s",
            (payment_id,)
        )

        conn.commit()

    print(f"Updated {len(data)} records in the 'Log' table of the ZD database to be validated. \n")



# ------------- Message Queue functions ------------- #

def on_receive_message(ch, method, properties, body):
    # Connect to the DB
    conn = connect_to_db(host='192.168.0.24', dbname='db', user='postgres', password='postgres')

    data = None

    try:
        # Decode the JSON string back into a Python list
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"Received empty message. Starting to retrieve data from the 'Log' table of the ZD database.")

    # if there is data in the body, the message comes back from the listen.py script of the validator
    # and is supposed to trigger the updating of the 'Log' table
    if data and len(data) > 0:
        update_log(conn, data)

    else:
        # retrieve the data from the 'Log' table
        log_data = get_data_from_log(conn)

        if len(log_data) > 0:

            # Convert the successfully inserted data to a JSON string
            message = json.dumps(log_data)

            # Send the message to the queue
            ch.basic_publish(exchange='', routing_key='zd-to-validator', body=message)
            print(f"{len(log_data)} unvalidated rows sent back to the validator service via the zd-to-validator queue. \n")

        else:
            print(f"No unvalidated rows found in the 'Log' table of the ZD database. \n")

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
    channel.queue_declare(queue='validator-to-zd')

    # Declare the callback function
    channel.basic_consume(queue='validator-to-zd', on_message_callback=on_receive_message, auto_ack=False)

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