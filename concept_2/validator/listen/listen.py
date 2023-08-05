"""
This script is run inside the validator-listen container.

It listens for messages from both the EPLF and ZD via the message queue,
which contain the unvalidated data from their respective 'Log' tables.

These records then get compared and the matches get sent back to the EPLF and ZD via the message queue,
so they can update the 'validated' field in their 'Log' tables accordingly.
"""


import json
import time
from datetime import datetime
import pika


# Global variables to store incoming data
eplf_data = []
zd_data = []
successful_matches = []



# ------------- Message Queue receive functions ------------- #

def on_receive_eplf_message(ch, method, properties, body):
    # whenever a message is received on the validator-to-eplf queue, store it in the eplf_data list
    global eplf_data
    data = None

    try:
        # Decode the JSON string back into a Python list
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"Received empty message from the EPLF. \n")

    if data:
        eplf_data = data

        print(f"Received {len(data)} rows from the EPLF. \n")


def on_receive_zd_message(ch, method, properties, body):
    # whenever a message is received on the validator-to-zd queue, store it in the zd_data list
    global zd_data
    data = None

    try:
        # Decode the JSON string back into a Python list
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"Received empty message from the ZD. \n")

    if data:
        zd_data = data

        print(f"Received {len(data)} rows from the ZD. \n")


def compare_data():
    global eplf_data
    global zd_data
    global successful_matches

    # Iterate through both data lists
    for eplf_row in eplf_data:
        for zd_row in zd_data:

            # If the rows match, store them in the successful_matches list
            if eplf_row == zd_row:
                successful_matches.append(eplf_row)

    # Reset the data lists for the next round of messages
    eplf_data = []
    zd_data = []



# ------------- Message Queue publish functions ------------- #

def send_eplf_matches(channel, matches):
    # Convert the matches to JSON format
    matches_json = json.dumps(matches)

    # Publish the matches to the EPLF queue
    channel.basic_publish(exchange='', routing_key='validator-to-eplf', body=matches_json)

    print(f"Sent {len(matches)} rows to be validated back to the EPLF via the validator-to-eplf queue. \n")


def send_zd_matches(channel, matches):
    # Convert the matches to JSON format
    matches_json = json.dumps(matches)

    # Publish the matches to the ZD queue
    channel.basic_publish(exchange='', routing_key='validator-to-zd', body=matches_json)

    print(f"Sent {len(matches)} rows to be validated back to the ZD via the validator-to-zd queue. \n")



# ------------- Main function ------------- #

def main():
    # Tell python to use the global variables
    global eplf_data, zd_data, successful_matches

    # Provide authentication for the mq
    credentials = pika.PlainCredentials('rabbit', 'rabbit')

    # Creating the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.0.22', credentials=credentials, heartbeat=65535))

    # Create the EPLF channel and queue
    validator_to_eplf_channel = connection.channel()
    validator_to_eplf_channel.queue_declare(queue='validator-to-eplf')

    # Create the EPLF to validator channel and queue
    eplf_to_validator_channel = connection.channel()
    eplf_to_validator_channel.queue_declare(queue='eplf-to-validator')

    # Create the ZD validation channel and queue
    validator_to_zd_channel = connection.channel()
    validator_to_zd_channel.queue_declare(queue='validator-to-zd')

    # Create the ZD to validator channel and queue
    zd_to_validator_channel = connection.channel()
    zd_to_validator_channel.queue_declare(queue='zd-to-validator')

    # Todo: fix

    print('Waiting for messages. To exit press CTRL+C')

    try:
        # Create an infinite loop
        while True:

            # Consume one message at a time from each channel
            eplf_method, eplf_properties, eplf_body = eplf_to_validator_channel.basic_get(queue='eplf-to-validator', auto_ack=True)
            zd_method, zd_properties, zd_body = zd_to_validator_channel.basic_get(queue='zd-to-validator', auto_ack=True)

            # If a message was received, process it
            if eplf_method:
                on_receive_eplf_message(eplf_to_validator_channel, eplf_method, eplf_properties, eplf_body)

            if zd_method:
                on_receive_zd_message(zd_to_validator_channel, zd_method, zd_properties, zd_body)

            # Check if both lists have data
            if eplf_data and zd_data:
                compare_data()

                # If there were successful matches, send them back to both services to have them update their 'Log' tables
                if successful_matches:
                    send_eplf_matches(validator_to_eplf_channel, successful_matches)
                    send_zd_matches(validator_to_zd_channel, successful_matches)

                    # Reset the successful_matches list for the next round of messages
                    successful_matches = []

            # Messages from the EPLF and ZD should come in about every minute at roughly the same time
            # so checking for new messages every 30 seconds should be sufficient
            time.sleep(30)

    except KeyboardInterrupt:
        # CTRL+C closes the connection
        connection.close()


if __name__ == '__main__':
    main()