import requests
import json
import time
from confluent_kafka import Producer

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',  # Use the actual IP address
    'client.id': 'user-producer'
}

# Create a Kafka producer instance
producer = Producer(producer_config)

# RandomUser API endpoint with your API key
api_key = 'WZV9-2S7O-9BH3-3YAH'
random_user_api_url = f'https://randomuser.me/api'

# Function to fetch user data from the RandomUser API with batch collection and pauses
def fetch_random_user_with_batches(batch_size=30, pause_duration=1):
    request_count = 0
    while True:
        batch = []
        for _ in range(batch_size):
            response = requests.get(random_user_api_url)
            if response.status_code == 200:
                user_data = response.json()
                batch.append(json.dumps(user_data))
                request_count += 1
            else:
                print(f"Request failed. Retrying...")
        
        if batch:
            for data in batch:
                # Produce the user data to the Kafka topic
                producer.produce(kafka_topic, key=None, value=data)
                producer.flush()
                print(f"Produced user data to Kafka ({request_count}/{batch_size}): {data}")

        if request_count >= batch_size:
            print(f"Pausing for {pause_duration} seconds...")
            time.sleep(pause_duration)
            request_count = 0

# Kafka topic to produce data to
kafka_topic = 'user_data'

# Start collecting data in batches with pauses
fetch_random_user_with_batches()
