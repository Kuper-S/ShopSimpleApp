
from flask import Flask, jsonify, request
from pymongo import MongoClient
from kafka import KafkaConsumer, KafkaProducer
import threading
import json
import os

app = Flask(__name__)
# Setting IP's in dy
# Setting IP's in dy
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
#KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'my-kafka.default.svc.cluster.local:9092')


kafka_sasl_mechanism = os.getenv('KAFKA_SASL_MECHANISM')
kafka_security_protocol = os.getenv('KAFKA_SECURITY_PROTOCOL')
kafka_sasl_username = os.getenv('KAFKA_SASL_USERNAME')
kafka_sasl_password = os.getenv('KAFKA_SASL_PASSWORD')

# MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['shop_db']
users_collection = db['users']
items_collection = db['items']

# Kafka setup
consumer = KafkaConsumer(
    'purchase_topic',
    'get_all_bought_items',
    bootstrap_servers=KAFKA_BROKER,
    security_protocol=kafka_security_protocol,
    sasl_mechanism=kafka_sasl_mechanism,
    sasl_plain_username=kafka_sasl_username,
    sasl_plain_password=kafka_sasl_password,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    security_protocol=kafka_security_protocol,
    sasl_mechanism=kafka_sasl_mechanism,
    sasl_plain_username=kafka_sasl_username,
    sasl_plain_password=kafka_sasl_password,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/items', methods=['GET'])
def get_items():
    items = list(items_collection.find({}, {'_id': 0}))
    return jsonify(items), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find({}, {'_id': 0}))
    return jsonify(users), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_collection.find_one({'userID': user_id}, {'_id': 0})
    if user and 'totalCost' not in user:
        user['totalCost'] = 0  # Ensure the totalCost field is present
    return jsonify(user), 200

@app.route('/user/<user_id>/total_cost', methods=['GET'])
def get_user_total_cost(user_id):
    user = users_collection.find_one({'userID': user_id}, {'_id': 0})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    total_cost = user.get('totalCost', 0)
    return jsonify({'total_cost': total_cost}), 200

def consume_messages():
    for message in consumer:
        data = message.value
        if message.topic == 'purchase_topic':
            item = items_collection.find_one({'id': data['item_id']}, {'_id': 0})
            if item:
                item_price = item.get('price', 0)
                
                user_update = {
                    '$push': {'purchases': data['item_id']},
                    '$inc': {'totalCost': item_price}
                }
                
                users_collection.update_one(
                    {'userID': data['user_id']},
                    {'$setOnInsert': {'totalCost': 0}},  # Initialize totalCost if not present
                    upsert=True
                )
                
                users_collection.update_one(
                    {'userID': data['user_id']},
                    user_update,
                    upsert=True
                )
            else:
                print(f'Item not found: {data["item_id"]}')
        elif message.topic == 'get_all_bought_items':
            user_id = data.get('user_id')
            user = users_collection.find_one({'userID': user_id}, {'_id': 0})
            if user:
                purchases = user.get('purchases', [])
                response = {'user_id': user_id, 'purchases': purchases}
                producer.send('all_bought_items_response', value=response)

if __name__ == '__main__':
    threading.Thread(target=consume_messages, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
