import pytest
from services.order_services import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def create_product(client, name, price, quantity):
    # Helper function to create a product
    response = client.post('/product/create', json={'name': name, 'price': price, 'quantity': quantity})
    assert response.status_code == 201
    return response.json['product_id']

def test_create_product(client):
    # Test create product with valid data
    response = client.post('/product/create', json={'name': 'Test Product', 'price': 10.0, 'quantity': 5})
    assert response.status_code == 201
    assert 'product_id' in response.json

    # Test create product with missing data
    response = client.post('/product/create', json={'price': 10.0, 'quantity': 5})
    assert response.status_code == 400  

def test_search_product_by_name(client):
    # Test search product with valid name
    response = client.get('/products/search?name=test')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    # Test search product with empty name
    response = client.get('/products/search')
    assert response.status_code == 400  

def test_get_product(client):
    # Create a product
    product_id = create_product(client, 'Test Product', 10.0, 5)

    # Test get product with valid product_id
    response = client.get(f'/product/{product_id}')
    assert response.status_code == 200
    assert 'error' not in response.json

    # Test get product with invalid product_id format
    response = client.get('/product/invalid_product_id')
    assert response.status_code == 404


def test_list_products(client):
    # Test list products
    response = client.get('/products')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

  
def test_add_to_and_get_and_remove_from_wishlist(client):
    # Create a product
    product_id = create_product(client, 'Test Product', 10.0, 5)

    # Test add product to wishlist with valid data
    response = client.post('/wishlist/add', json={'product_id': product_id, 'username': 'test_user'})
    assert response.status_code == 200
    assert 'error' not in response.json

   # Test add product to wishlist with invalid username
    response = client.post('/wishlist/add', json={'product_id': product_id, 'username': 'non_existing_user'})
    assert response.status_code == 404
    assert 'error' in response.json
    assert response.json['error'] == 'User not found'

    # Check if wishlist products can be retrieved
    response = client.get('/wishlist/products/test_user')
    assert response.status_code == 200
    if response.json:  # Check if response.json is not None
        assert 'error' not in response.json
    # Test get wishlist products with non-existing username
    response = client.get('/wishlist/products/non_existing_user')
    assert response.status_code == 404
    assert 'error' in response.json
    assert response.json['error'] == 'User not found'

    # Test remove product from wishlist with invalid product_id
    response = client.post('/wishlist/remove', json={'product_id': 'invalid_product_id', 'username': 'test_user'})
    assert response.status_code == 404
    assert 'error' in response.json
    assert response.json['error'] == 'Product not found in wishlist'

    # Test remove product from wishlist with valid data
    response = client.post('/wishlist/remove', json={'product_id': product_id, 'username': 'test_user'})
    assert response.status_code == 200
    assert 'error' not in response.json
    


def test_update_product(client):
    # Create a product
    product_id = create_product(client, 'Test2', 10.0, 5)

    # Test update product with valid product_id and data
    response = client.put(f'/product/update/{product_id}', json={'name': 'Test2', 'price': 11.0, 'quantity': 10, 'version': 1})
    assert response.status_code == 200
    assert 'message' in response.json

    # Test update product with invalid version
    response = client.put(f'/product/update/{product_id}', json={'name': 'Updated Product', 'price': 15.0, 'quantity': 10, 'version': 1})
    assert response.status_code == 409
    assert 'error' in response.json
    assert response.json['error'] == 'Conflict: Product has been modified by another user'
