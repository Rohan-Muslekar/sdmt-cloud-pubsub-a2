from google.cloud import pubsub_v1      # pip install google-cloud-pubsub  ##to install
import glob                             # for searching for json file
import json
import os
import csv

# Search the current directory for the JSON file (including the service account key)
# to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

# Set the project_id with your project ID
project_id="my-first-test-235715";
topic_name = "meterLabels";   # change it for your topic name if needed
csv_file = "design/Labels.csv";

# create a publisher and get the topic path for the publisher.
# ordering is enabled so that all the readings of one device arrive in the
# order they were published.
publisher = pubsub_v1.PublisherClient(
    publisher_options=pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
)
topic_path = publisher.topic_path(project_id, topic_name)
print(f"Publishing the records of {csv_file} to {topic_path}.")

# the numeric columns of the CSV. A blank cell means the meter did not report
# that measurement, so it becomes None, the same way smartMeter.py drops readings.
numeric_fields = ["time", "temperature", "humidity", "pressure"]

def to_record(row):
    record = dict(row)
    for field in numeric_fields:
        record[field] = float(record[field]) if record[field] else None
    return record

published = 0
with open(csv_file, newline='') as f:
    # read the CSV file, each row is read as a dictionary keyed by the header
    for row in csv.DictReader(f):
        record = to_record(row)

        record_value = json.dumps(record).encode('utf-8')   # serialize the record

        try:
            # the device name is used as the ordering key
            future = publisher.publish(topic_path, record_value,
                                       ordering_key=record["profileName"])

            # ensure that the publishing has been completed successfully
            future.result()
            published += 1
            print("The record {} has been published successfully".format(record))
        except Exception as error:
            print("Failed to publish the record: {}".format(error))

print("{} records published to {}".format(published, topic_name))
