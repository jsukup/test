import pytest
import json
import os
import sys

# Add app directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test the home endpoint returns correct response"""
    response = client.get('/')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'message' in data

def test_health_endpoint(client):
    """Test the health endpoint returns correct response"""
    response = client.get('/health')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['status'] == 'healthy'

def test_login_endpoint_success(client):
    """Test the login endpoint with correct credentials"""
    response = client.post('/api/auth/login',
                       data=json.dumps({'username': 'user', 'password': 'password'}),
                       content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'access_token' in data

def test_login_endpoint_failure(client):
    """Test the login endpoint with incorrect credentials"""
    response = client.post('/api/auth/login',
                       data=json.dumps({'username': 'wrong', 'password': 'wrong'}),
                       content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 401
    assert data['success'] == False

def test_predict_endpoint_no_auth(client):
    """Test predict endpoint without authentication"""
    response = client.post('/api/v1/predict',
                       data=json.dumps({'features': [0, 1]}),
                       content_type='application/json')
    
    assert response.status_code == 401  # Unauthorized

def test_predict_endpoint_with_auth(client):
    """Test predict endpoint with authentication"""
    # First get an auth token
    auth_response = client.post('/api/auth/login',
                           data=json.dumps({'username': 'user', 'password': 'password'}),
                           content_type='application/json')
    auth_data = json.loads(auth_response.data)
    token = auth_data['access_token']
    
    # Make prediction request with token
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/v1/predict',
                       data=json.dumps({'features': [0, 1]}),
                       content_type='application/json',
                       headers=headers)
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'prediction' in data
    assert 'probability' in data
    assert data['features'] == [0, 1]

def test_invalid_input(client):
    """Test predict endpoint with invalid input"""
    # First get an auth token
    auth_response = client.post('/api/auth/login',
                           data=json.dumps({'username': 'user', 'password': 'password'}),
                           content_type='application/json')
    auth_data = json.loads(auth_response.data)
    token = auth_data['access_token']
    
    # Make prediction request with token and invalid input
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/v1/predict',
                       data=json.dumps({'features': [0, 1, 2]}),  # Invalid: too many features
                       content_type='application/json',
                       headers=headers)
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] == False
    assert 'error' in data 