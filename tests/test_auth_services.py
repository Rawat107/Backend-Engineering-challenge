import pytest
from services.auth_services import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_user(client):
    # Test registration with valid data
    response = client.post('/register', json={'username': 'test_user', 'password': 'password'})
    assert response.status_code == 201
    assert 'message' in response.json
    print("Register User Test Passed")

    # Test registration with existing username
    response = client.post('/register', json={'username': 'test_user', 'password': 'password'})
    assert response.status_code == 400
    assert 'error' in response.json
    print("Register User with Existing Username Test Passed")

def test_login_user(client):
    # Register a user for login testing
    client.post('/register', json={'username': 'test_user', 'password': 'password'})

    # Test login with correct credentials
    response = client.post('/login', json={'username': 'test_user', 'password': 'password'})
    assert response.status_code == 200
    if response.json is not None:  
        assert 'message' in response.json
    print("Login with Correct Credentials Test Passed")

    # Test login with incorrect password
    response = client.post('/login', json={'username': 'test_user', 'password': 'wrong_password'})
    assert response.status_code == 401
    if response.json is not None:  
        assert 'error' in response.json
    print("Login with Incorrect Password Test Passed")

    # Test login with non-existing user
    response = client.post('/login', json={'username': 'non_existing_user', 'password': 'password'})
    assert response.status_code == 401
    if response.json is not None:  
        assert 'error' in response.json
    print("Login with Non-existing User Test Passed")

    # Test login without username
    response = client.post('/login', json={'password': 'password'})
    assert response.status_code == 400
    if response.json is not None:  
        assert 'error' in response.json
    print("Login without Username Test Passed")

