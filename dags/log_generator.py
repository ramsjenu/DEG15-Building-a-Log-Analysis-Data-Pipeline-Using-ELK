from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
import logging
import random

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 14),
    'retries': 3,  # Retry the task 3 times in case of failure
    'retry_delay': timedelta(minutes=5),  # Delay between retries
    'execution_timeout': timedelta(minutes=15),  # Task timeout increased to 15 minutes
}

log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']

# Instantiate the DAG
dag = DAG(
    'kafka_log_producer',
    default_args=default_args,
    description='A DAG to produce logs and send them to Kafka',
    schedule_interval=timedelta(minutes=10),
)

# Function to generate and send a log message to Kafka
def generate_and_send_log(**context):
    producer = KafkaProducer(
        bootstrap_servers='broker:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    log_message = {
        'timestamp': datetime.now().timestamp(),
        'level': random.choice(log_levels),
     #   'level': 'ERROR',
        'message': 'This is a test log message',
        'service': 'auth-service'
    }

    # Send the log message to Kafka
    future = producer.send('logs', value=log_message)

    try:
        # Flush the producer to make sure the message is sent (with a longer timeout)
        producer.flush(timeout=30)  # Increased Kafka producer flush timeout
        logging.info(f"Successfully sent log to Kafka: {log_message}")
    except Exception as e:
        logging.error(f"Failed to send log to Kafka: {e}")
        raise e
    finally:
        producer.close()

# Define the PythonOperator that will execute the `generate_and_send_log` function
send_log_to_kafka = PythonOperator(
    task_id='send_log_to_kafka',
    python_callable=generate_and_send_log,
    provide_context=True,
    dag=dag,
)

# Set task dependencies (if there are more tasks, you can set upstream/downstream)
send_log_to_kafka
