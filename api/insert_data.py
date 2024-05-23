import os
from pymongo import MongoClient

# Set MongoDB URI from environment variable
mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/')
client = MongoClient(mongo_uri)
db = client['shop_db']

# Insert Users
users = [
    {
        "userID": "user1",
        "userName": "Kuper",
        "purchases": []
    },
    {
        "userID": "user2",
        "userName": "Bar",
        "purchases": []
    },
    {
        "userID": "user3",
        "userName": "Nick",
        "purchases": []
    },
    {
        "userID": "user4",
        "userName": "Diana",
        "purchases": []
    },
    {
        "userID": "user5",
        "userName": "Slavik",
        "purchases": []
    },
    {
        "userID": "user6",
        "userName": "Danny",
        "purchases": []
    }
]

for user in users:
    db.users.update_one(
        {"userID": user["userID"]},
        {"$set": user},
        upsert=True
    )

# Insert Items
items = [
    {
        "id": "item1",
        "name": "Xbox",
        "price": 299.99
    },
    {
        "id": "item2",
        "name": "PlayStation",
        "price": 499.99
    },
    {
        "id": "item3",
        "name": "PC",
        "price": 999.99
    },
    {
        "id": "item4",
        "name": "Camera",
        "price": 199.99
    },
    {
        "id": "item5",
        "name": "Headphones",
        "price": 89.99
    },
    {
        "id": "item6",
        "name": "Smartphone",
        "price": 799.99
    }
]

for item in items:
    db.items.update_one(
        {"id": item["id"]},
        {"$set": item},
        upsert=True
    )

print("Data inserted successfully!")