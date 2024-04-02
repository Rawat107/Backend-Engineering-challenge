from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from bson import ObjectId, json_util
from json import dumps
import json

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
orders_collection = db['orders']
products_collection = db['products']

@app.route('/order/create', methods=['POST'])
def create_order():
    data = request.json
    if 'product_id' not in data or 'username' not in data or 'quantity' not in data:
        abort(400, description="Product ID, username, and quantity are required")

    product_id = data['product_id']
    username = data['username']
    quantity = data['quantity']

    # Check if the product exists and has sufficient quantity
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    if product['quantity'] < quantity:
        return jsonify({'error': 'Insufficient quantity available'}), 400

    # Reduce the product quantity in the database
    products_collection.update_one({'_id': ObjectId(product_id)}, {'$inc': {'quantity': -quantity}})

    # Create the order
    order = {
        'product_id': product_id,
        'username': username,
        'quantity': quantity,
        'status': 'pending'
    }
    order_id = orders_collection.insert_one(order).inserted_id
    return jsonify({'message': 'Order created successfully', 'order_id': str(order_id)}), 201

@app.route('/order/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_collection.find_one({'_id': ObjectId(order_id)})
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order['_id'] = str(order['_id'])  

    serialized_order = dumps(order)
    return jsonify(json.loads(serialized_order)), 200 

@app.route('/order/update/<order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    if 'status' not in data:
        abort(400, description="Status is required to update order")

    status = data['status']
    valid_statuses = ['pending', 'delivered']
    if status not in valid_statuses:
        return jsonify({'error': 'Invalid status. Status must be either "pending" or "delivered"'}), 400

    order = orders_collection.find_one({'_id': ObjectId(order_id)})
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': status}})
    return jsonify({'message': 'Order updated successfully'}), 200

@app.route('/orders', methods=['GET'])
def list_orders():
    orders = list(orders_collection.find())
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(debug=True)
