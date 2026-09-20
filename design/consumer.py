from google.cloud import pubsub_v1      # pip install google-cloud-pubsub  ##to install
import glob                             # for searching for json file
import json
import os

# Search the current directory for the JSON file (including the service account key)
# to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

# Set the project_id with your project ID
project_id="my-first-test-235715";
topic_name = "meterLabels";   # change it for your topic name if needed
subscription_id = "meterLabels-sub";   # change it for your subscription name if needed

# create a subscriber to the subscription of the project using the subscription_id
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
topic_path = 'projects/{}/topics/{}'.format(project_id,topic_name);

print(f"Listening for messages on {subscription_path}..\n")

count = 0

# Cloud Pub/Sub guarantees at-least-once delivery, so the same record can be
# delivered more than once. message_id is stable across redeliveries, so it is
# used to tell a redelivery apart from a new record.
seen = set()

# A callback function for handling received messages
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    global count
    # convert from bytes to dictionary (deserialization)
    record = json.loads(message.data.decode('utf-8'));
    count += 1
    duplicate = message.message_id in seen
    seen.add(message.message_id)

    # print the values of the dictionary
    print("Record {}: {}{}".format(len(seen), list(record.values()),
                                   "   [redelivery]" if duplicate else ""))

    # Report to Google Pub/Sub the successful processing of the received message
    message.ack()

with subscriber:
    # The callback function will be called for each message received from the topic
    # through the subscription.
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        print("\nStopped after {} deliveries, {} unique records.".format(count, len(seen)))
