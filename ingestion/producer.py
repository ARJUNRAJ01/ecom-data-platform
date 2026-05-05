"""
ingestion/producer.py
Generates fake data and sends it to Kafka for all 4 sources.
Run: python ingestion/producer.py
"""

import json, time, uuid, random
from datetime import datetime, timezone
from confluent_kafka import Producer
from faker import Faker

fake = Faker()
producer = Producer({"bootstrap.servers": "localhost:9092"})

PRODUCTS   = [f"PROD-{i:04d}" for i in range(1, 500)]
CUSTOMERS  = [f"CUST-{i:05d}" for i in range(1, 10000)]
CATEGORIES = ["electronics", "fashion", "grocery", "furniture", "beauty", "sports"]
PAGES      = ["/home", "/product", "/cart", "/checkout", "/search", "/deals"]
PAYMENTS   = ["credit_card", "debit_card", "upi", "wallet", "cod"]

def send(topic, key, data):
    producer.produce(topic, key=key, value=json.dumps(data, default=str))
    producer.poll(0)

def web_log():
    event_type = random.choice(["page_view", "search", "click", "add_to_cart"])
    d = {
        "event_id":      str(uuid.uuid4()),
        "customer_id":   random.choice(CUSTOMERS),
        "event_type":    event_type,
        "page":          random.choice(PAGES),
        "device":        random.choice(["mobile", "desktop", "tablet"]),
        "ip":            fake.ipv4_public(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if event_type == "search":
        d["search_query"] = fake.word()
    if event_type in ("click", "add_to_cart"):
        d["product_id"] = random.choice(PRODUCTS)
        d["category"]   = random.choice(CATEGORIES)
    return d

def transaction():
    return {
        "order_id":      f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "customer_id":   random.choice(CUSTOMERS),
        "event_type":    random.choice(["ORDER_PLACED", "PAYMENT_DONE", "SHIPPED", "DELIVERED", "RETURNED"]),
        "amount_inr":    round(random.uniform(99, 49999), 2),
        "discount_inr":  round(random.uniform(0, 500), 2),
        "payment_type":  random.choice(PAYMENTS),
        "city":          fake.city(),
        "product_id":    random.choice(PRODUCTS),
        "category":      random.choice(CATEGORIES),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

def review():
    rating = random.choices([1,2,3,4,5], weights=[5,8,12,30,45])[0]
    return {
        "review_id":   f"REV-{uuid.uuid4().hex[:8].upper()}",
        "customer_id": random.choice(CUSTOMERS),
        "product_id":  random.choice(PRODUCTS),
        "category":    random.choice(CATEGORIES),
        "rating":      rating,
        "sentiment":   "positive" if rating >= 4 else ("neutral" if rating == 3 else "negative"),
        "body":        fake.sentence(nb_words=12),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

def social():
    return {
        "post_id":        f"POST-{uuid.uuid4().hex[:8].upper()}",
        "platform":       random.choice(["twitter", "facebook", "instagram"]),
        "product_id":     random.choice(PRODUCTS),
        "action_type":    random.choice(["like", "share", "comment", "mention"]),
        "likes":          random.randint(0, 5000),
        "is_influencer":  random.random() < 0.05,
        "engagement":     round(random.uniform(0.01, 0.95), 3),
        "timestamp_utc":  datetime.now(timezone.utc).isoformat(),
    }

if __name__ == "__main__":
    print("Producing events to Kafka... Ctrl+C to stop")
    count = 0
    while True:
        send("ecom.web-logs",     str(uuid.uuid4()), web_log())
        send("ecom.transactions", str(uuid.uuid4()), transaction())
        if count % 5 == 0:   # reviews are less frequent
            send("ecom.reviews",  str(uuid.uuid4()), review())
        if count % 8 == 0:   # social even less
            send("ecom.social",   str(uuid.uuid4()), social())
        count += 1
        if count % 100 == 0:
            producer.flush()
            print(f"  Sent {count} events")
        time.sleep(0.01)
