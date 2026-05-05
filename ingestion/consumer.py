"""
ingestion/consumer.py
Reads from all 4 Kafka topics and saves data as Parquet files.
Parquet files are what dbt + DuckDB will read from.
Run: python ingestion/consumer.py
"""

import json, os
from datetime import datetime, timezone
from confluent_kafka import Consumer
import pandas as pd

PARQUET_DIR = "data/parquet"
os.makedirs(PARQUET_DIR, exist_ok=True)

TOPICS = ["ecom.web-logs", "ecom.transactions", "ecom.reviews", "ecom.social"]

TOPIC_MAP = {
    "ecom.web-logs":     "web_logs",
    "ecom.transactions": "transactions",
    "ecom.reviews":      "reviews",
    "ecom.social":       "social_feeds",
}

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id":          "ecom-parquet-writer",
    "auto.offset.reset": "earliest",
})
consumer.subscribe(TOPICS)

buffers = {name: [] for name in TOPIC_MAP.values()}
FLUSH_EVERY = 500   # write to parquet every 500 records per topic

def flush_to_parquet(name, records):
    if not records:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    path  = f"{PARQUET_DIR}/{name}_{today}.parquet"
    df_new = pd.DataFrame(records)
    if os.path.exists(path):
        df_old = pd.read_parquet(path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_parquet(path, index=False)
    print(f"  Saved {len(df_new)} records → {path} (total: {len(df)})")

if __name__ == "__main__":
    print("Consumer running... reading from Kafka → Parquet files")
    print(f"Files saved to: {PARQUET_DIR}/")
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Error: {msg.error()}")
                continue
            topic = msg.topic()
            name  = TOPIC_MAP.get(topic)
            if not name:
                continue
            try:
                record = json.loads(msg.value().decode("utf-8"))
                record["_ingest_date"] = datetime.now(timezone.utc).date().isoformat()
                buffers[name].append(record)
            except Exception as e:
                print(f"Parse error: {e}")
                continue

            if len(buffers[name]) >= FLUSH_EVERY:
                flush_to_parquet(name, buffers[name])
                buffers[name] = []

    except KeyboardInterrupt:
        print("\nFlushing remaining records...")
        for name, records in buffers.items():
            flush_to_parquet(name, records)
        consumer.close()
        print("Done.")
