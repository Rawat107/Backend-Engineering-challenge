from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
products_collection = db['products']
users_collection = db['user']

# Create text index for search functionality
products_collection.create_index([('name', 'text')])

# Search Product
@app.route('/products/search', methods=['GET'])
def search_product_by_name():
    name = request.args.get('name')

    if not name:
        abort(400, description="Query parameter 'name' is required")

    # Search for products by name
    products = list(products_collection.find({'name': {'$regex': name, '$options': 'i'}}))
    if not products:
        return jsonify({'error': f"No products found with name '{name}'"}), 404

    # Convert ObjectId to string representation
    for product in products:
        product['_id'] = str(product['_id'])

    # Serialize the list of products to JSON
    serialized_products = dumps(products)

    return serialized_products, 200, {'Content-Type': 'application/json'}

# Get Product
@app.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        # Attempt to convert product_id to ObjectId
        product_oid = ObjectId(product_id)
    except Exception as e:
        # Return 404 if product_id is not a valid ObjectId
        return jsonify({'error': 'Invalid product ID format'}), 404

    product = products_collection.find_one({'_id': product_oid})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product['_id'] = str(product['_id'])  # Convert ObjectId to string
    return jsonify(product), 200

# Create Product
@app.route('/product/create', methods=['POST'])
def create_product():
    data = request.json
    if 'name' not in data or 'price' not in data or 'quantity' not in data:
        abort(400, description="Name, price, and quantity are required")

    name = data['name']
    price = data['price']
    quantity = data['quantity']

    # Insert new product into the database with default version 0
    product_id = products_collection.insert_one({'name': name, 'price': price, 'quantity': quantity, 'version': 0}).inserted_id
    return jsonify({'message': 'Product created successfully', 'product_id': str(product_id)}), 201



@app.route('/products', methods=['GET'])
def list_products():
    products = list(products_collection.find())
    if not products:
        return jsonify({'error': 'No products found'}), 404

    # Convert ObjectId to string representation
    for product in products:
        product['_id'] = str(product['_id'])

    # Serialize the list of products to JSON
    serialized_products = dumps(products)

    return serialized_products, 200, {'Content-Type': 'application/json'}

# Add Product to Wishlist
@app.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    data = request.json
    if 'product_id' not in data or 'username' not in data:
        abort(400, description="Both product_id and username are required")

    product_id = data['product_id']
    username = data['username']

    # Find the user in the database
    print(f"Searching for user: {username}")
    user = users_collection.find_one({'username': username})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if the product exists
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Add the product to the user's wishlist
    if 'wishlist' not in user:
        user['wishlist'] = []

    if product_id in user['wishlist']:
        return jsonify({'error': 'Product already in wishlist'}), 400

    user['wishlist'].append(product_id)
    users_collection.update_one({'username': username}, {'$set': {'wishlist': user['wishlist']}})

    return jsonify({'message': 'Product added to wishlist successfully'}), 200
 
# Get Wishlist Products
@app.route('/wishlist/products/<username>', methods=['GET'])
def get_wishlist_products(username):
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    wishlist_products = []
    if 'wishlist' in user:
        for product_id in user['wishlist']:
            product = products_collection.find_one({'_id': ObjectId(product_id)})
            if product:
                wishlist_products.append({'username': username, 'product': product})
    serialized_wishlist = dumps(wishlist_products)
    return serialized_wishlist, 200
 
# Remove Product from Wishlist
@app.route('/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    data = request.json
    if 'product_id' not in data or 'username' not in data:
        abort(400, description='Both product_id and username are required')
    
    product_id = data['product_id']
    username = data['username']

    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'wishlist' in user:
        if product_id in user['wishlist']:
            user['wishlist'].remove(product_id)
            users_collection.update_one({'username': username}, {'$set': {'wishlist': user['wishlist']}})
            return jsonify({'message': 'Product removed from wishlist successfully'})
        else:
            return jsonify({'error': 'Product not found in wishlist'}), 404
    else:
        return jsonify({'error': 'User does not have a wishlist'}), 404

# Update Product
@app.route('/product/update/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    if 'name' not in data or 'price' not in data or 'quantity' not in data or 'version' not in data:
        abort(400, description="Name, price, quantity, and version are required for update")

    name = data['name']
    price = data['price']
    quantity = data['quantity']
    version = data['version']

    # Check if the product exists
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Check if the version matches
    if product.get('version') == version:
        return jsonify({'error': 'Conflict: Product has been modified by another user'}), 409

    # Update the product data and increment the version
    products_collection.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': {'name': name, 'price': price, 'quantity': quantity}, '$inc': {'version': 1}}
    )

    return jsonify({'message': 'Product updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
