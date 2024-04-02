import pytest
from services.order_services import app
from pymongo import MongoClient
from bson import ObjectId
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def create_product(name, price, quantity):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ecommerce']
    product_id = db.products.insert_one({
        'name': name,
        'price': price,
        'quantity': quantity
    }).inserted_id
    client.close()
    return str(product_id)

def test_create_order(client):
    # Create a product in the database
    product_id = create_product('Test Product', 10.0, 10)

    # Make a POST request to create an order
    response = client.post('/order/create', json={
        'product_id': product_id,
        'username': 'test_user',
        'quantity': 5
    })

    # Check the response status code and message
    assert response.status_code == 201
    assert 'order_id' in response.json

def test_get_order(client):
    product_id = create_product('Test Product', 10.0, 10)

    # Make a POST request to create an order (using the API)
    response = client.post('/order/create', json={
        'product_id': product_id,
        'username': 'test_user',
        'quantity': 5
    })

    # Assert successful order creation
    assert response.status_code == 201
    assert 'order_id' in response.json

    # Extract the order ID from the response
    order_id = response.json['order_id']

    # Make a GET request to retrieve the order
    response = client.get(f'/order/{order_id}')
    # Check if response data is not None and does not contain an error
    assert response is not None
    assert 'error' not in response.json

def test_update_order(client):
    # Create a product in the database
    product_id = create_product('Test Product', 10.0, 10)

    # Insert an order into the database
    db = MongoClient('mongodb://localhost:27017/')['ecommerce']
    order_id = db.orders.insert_one({
        'product_id': product_id,
        'username': 'test_user',
        'quantity': 5,
        'status': 'pending'
    }).inserted_id

    # Make a PUT request to update the order status
    response = client.put(f'/order/update/{order_id}', json={'status': 'delivered'})

    # Check the response status code and message
    assert response.status_code == 200
    assert 'message' in response.json

def test_list_orders(client):
    # Make a GET request to retrieve all orders
    response = client.get('/orders')

    # Check the response status code
    assert response.status_code == 200

    # Parse the response content as JSON
    orders = response.json

    # Check if the parsed content is a list
    assert isinstance(orders, list)


if __name__ == '__main__':
    pytest.main()
