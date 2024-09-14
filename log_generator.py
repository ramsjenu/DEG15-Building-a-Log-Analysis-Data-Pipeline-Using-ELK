from kafka import KafkaProducer
import json
import random
import time

producer = KafkaProducer(bootstrap_servers=['broker:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']

def generate_log():
    return {
        'timestamp': time.time(),
        'level': random.choice(log_levels),
        'message': 'This is a test log message',
        'service': 'auth-service'
    }

while True:
    log = generate_log()
    print(f'Sending log: {log}')
    producer.send('logs', log)
    time.sleep(1)
