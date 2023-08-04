import json
import psycopg2
from psycopg2.extras import execute_values
import boto3
from datetime import date


def mask_data(data):
    # Mask device_id and ip
     # Check if 'device_id' key exists in the data
    if 'device_id' in data:
        # Mask device_id
        data["masked_device_id"] = f"MASKED_{data['device_id']}"
    else:
        # Handle the case when 'device_id' is missing
        data["masked_device_id"] = "UNKNOWN"

    # Check if 'ip' key exists in the data
    if 'ip' in data:
        # Mask ip
        data["masked_ip"] = f"MASKED_{data['ip']}"
    else:
        # Handle the case when 'ip' is missing
        data["masked_ip"] = "UNKNOWN"

    return data

def process_data():
    session = boto3.session.Session(aws_access_key_id='dummy_access_key', aws_secret_access_key='dummy_secret_key')
    sqs = session.resource('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')
    queue = sqs.get_queue_by_name(QueueName='login-queue') 

    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgres",
        database="postgres",
    )

    with conn.cursor() as cur:
            while True:
                messages = queue.receive_messages(MaxNumberOfMessages=10)
                if not messages:
                    break

                data_to_insert = []
                for message in messages:
                    try:
                        body = json.loads(message.body)
                        
                        if "user_id" not in body or "device_type" not in body:
                            print("Invalid message format:", body)
                            continue  # Skip processing this message
                            
                        masked_data = mask_data(body)
                        masked_data.setdefault("create_date", str(date.today()))
                        app_version = masked_data.get("app_version", 0)
                        try:
                            app_version = int(app_version)  # Convert app_version to an integer
                        except ValueError:
                            app_version = 0  # Set to 0 if the conversion fails
                            
                        # Check if 'user_id' key exists in the masked_data
                        if 'user_id' not in masked_data:
                            print("Missing 'user_id' in the message:", message.body)
                            continue  # Skip processing this message

                        flattened_data = {
                            "user_id": masked_data["user_id"],
                            "device_type": masked_data["device_type"],
                            "masked_ip": masked_data["masked_ip"],
                            "masked_device_id": masked_data["masked_device_id"],
                            "locale": masked_data["locale"],
                            "app_version": app_version,
                            "create_date": masked_data["create_date"]
                        }
                        data_to_insert.append(tuple(flattened_data.values()))
                    except json.JSONDecodeError:
                        print("Failed to process message:", message.body)

                        

                # Insert data into the PostgreSQL database
                if data_to_insert:
                    execute_values(cur, """
                        INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                        VALUES %s
                    """, data_to_insert)

                # Delete processed messages from the queue
                for message in messages:
                    message.delete()
    conn.close()

if __name__ == "__main__":
    process_data()
