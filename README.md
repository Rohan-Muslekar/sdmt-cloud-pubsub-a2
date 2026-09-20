# SOFE4630U Milestone 1: Data Ingestion with Cloud Pub/Sub

Coursework for ENGR 5520G / SOFE4630U, Ontario Tech University.
Based on the lab at [MohammadYasserZaki/SOFE4630U-MS1](https://github.com/MohammadYasserZaki/SOFE4630U-MS1).

GCP project: `my-first-test-235715`

| Topic | Subscription | Used by |
| --- | --- | --- |
| `testTopic` | `testTopic-sub` | `v1/` string messages typed by hand |
| `smartMeter` | `smartMeter-sub` | `v2/` simulated smart meter |
| `meterLabels` | `meterLabels-sub` (ordered) | `design/` records read from `Labels.csv` |

## Setup

The service account key is **not** in this repository. Put your own
`*.json` key in the repository root; every script finds it with
`glob("*.json")` and exports it as `GOOGLE_APPLICATION_CREDENTIALS`.

The service account needs `roles/pubsub.editor` on the project.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Running

Run everything **from the repository root**, so the `glob("*.json")` in each
script finds the key. Use two terminals, consumer first.

```bash
# part 3 and 4: type strings, watch them arrive
.venv/bin/python v1/consumer.py
.venv/bin/python v1/producer.py

# part 5: simulated meter, Ctrl+C to stop
.venv/bin/python v2/consumer.py
.venv/bin/python v2/smartMeter.py

# design: 100 records from Labels.csv
.venv/bin/python design/consumer.py
.venv/bin/python design/producer.py
```

## Design part

`design/producer.py` reads `design/Labels.csv` with `csv.DictReader`, turns each
row into a dictionary, serializes it with `json.dumps`, and publishes it to
`meterLabels`. Blank cells become `None`, matching the way `v2/smartMeter.py`
drops readings. Each message carries the device name (`profileName`) as its
ordering key, so readings from one device are delivered in publication order.

`design/consumer.py` subscribes to `meterLabels-sub`, deserializes each message
with `json.loads`, prints the dictionary values, and acknowledges the message.

See `REPORT.md` for the discussion answers and the full design writeup.
