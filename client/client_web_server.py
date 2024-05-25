from flask import Flask, request, jsonify, render_template
from kafka import KafkaProducer, KafkaConsumer
import threading
import requests
import json
import os

app = Flask(__name__)
#Setting IP's in a dynamic way.
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'my-kafka.default.svc.cluster.local:9092')
API_SERVER_URL = os.getenv('API_SERVER_URL', 'http://api-server:5000')


kafka_sasl_mechanism = os.getenv('KAFKA_SASL_MECHANISM')
kafka_security_protocol = os.getenv('KAFKA_SECURITY_PROTOCOL')
kafka_sasl_username = os.getenv('KAFKA_SASL_USERNAME')
kafka_sasl_password = os.getenv('KAFKA_SASL_PASSWORD')

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    security_protocol=kafka_security_protocol,
    sasl_mechanism=kafka_sasl_mechanism,
    sasl_plain_username=kafka_sasl_username,
    sasl_plain_password=kafka_sasl_password,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'all_bought_items_response',
    bootstrap_servers=KAFKA_BROKER,
    security_protocol=kafka_security_protocol,
    sasl_mechanism=kafka_sasl_mechanism,
    sasl_plain_username=kafka_sasl_username,
    sasl_plain_password=kafka_sasl_password,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/buy', methods=['POST'])
def buy_item():
    data = request.json
    producer.send('purchase_topic', value=data)
    producer.flush()
    return jsonify({'status': 'success'}), 200

@app.route('/items', methods=['GET'])
def get_items():
    response = requests.get(f'{API_SERVER_URL}/items')
    return jsonify(response.json()), 200

@app.route('/users', methods=['GET'])
def get_users():
    response = requests.get(f'{API_SERVER_URL}/users')
    return jsonify(response.json()), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    response = requests.get(f'{API_SERVER_URL}/user/{user_id}')
    return jsonify(response.json()), 200

@app.route('/get_all_bought_items', methods=['POST'])
def get_all_bought_items():
    data = request.json
    producer.send('get_all_bought_items', value=data)
    producer.flush()
    return jsonify({'status': 'request sent'}), 200

def consume_responses():
    for message in consumer:
        data = message.value
        print('Received response:', data)

if __name__ == '__main__':
    threading.Thread(target=consume_responses, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
