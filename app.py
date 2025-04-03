from flask import Flask, jsonify, request
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Set the logger level for Flask's logger
app.logger.setLevel(logging.INFO)

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, config=swagger_config)

# Configure Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Configure Caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# Create a simple ML model (this could be much more complex...)
def create_demo_model():
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 0])  
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Save model 
    if not os.path.exists('model.joblib'):
        joblib.dump(model, 'model.joblib')
    
    return model

# Load or create the model
model = create_demo_model()

# API Endpoints
@app.route('/')
@limiter.limit("10 per minute")
@cache.cached(timeout=60)
def hello():
    """Main endpoint that returns a greeting message"""
    app.logger.info('Main endpoint processing HTTP request')
    return jsonify({"success": True, "message": "Hello, Asling Partners! This is John, your new Applied AI Consultant."})

@app.route('/health', methods=['GET'])
@limiter.limit("60 per minute")
@cache.cached(timeout=10)
def health_check():
    """Health check endpoint to verify if the API is running"""
    app.logger.info('Health check endpoint called')
    return jsonify({"status": "healthy"})

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Login endpoint to get JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "user"
            password:
              type: string
              example: "password"
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    app.logger.info('Login endpoint called')
    if not request.is_json:
        app.logger.error('Invalid request: No JSON data provided')
        return jsonify({"success": False, "error": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    # In a real app, validate against a database
    # For demo purposes, accept simple credentials
    if username != 'user' or password != 'password':
        app.logger.warning(f'Failed login attempt for user: {username}')
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
    # Create token
    access_token = create_access_token(identity=username)
    app.logger.info(f'Successful login for user: {username}')
    return jsonify({"success": True, "access_token": access_token})

@app.route('/api/v1/predict', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def predict():
    """
    ML model inference endpoint
    ---
    tags:
      - Prediction
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - features
          properties:
            features:
              type: array
              items:
                type: number
              example: [0, 1]
    responses:
      200:
        description: Successful prediction
      400:
        description: Invalid input data
      401:
        description: Authentication failed
      500:
        description: Server error
    """
    current_user = get_jwt_identity()
    app.logger.info(f'Predict endpoint called by user: {current_user}')
    
    # Input validation
    if not request.json:
        app.logger.error('Invalid request: No JSON data provided')
        return jsonify({"success": False, "error": "Request must be JSON"}), 400
    
    try:
        # Extract features from request
        features = request.json.get('features')
        
        if not features:
            app.logger.error('Invalid request: No features provided')
            return jsonify({"success": False, "error": "No features provided"}), 400
        
        # Validate feature dimensions
        if len(features) != 2 or not all(isinstance(x, (int, float)) for x in features):
            app.logger.error('Invalid request: Features must be a list of 2 numbers')
            return jsonify({"success": False, "error": "Features must be a list of 2 numbers"}), 400
        
        # For caching, create a key based on the input features
        cache_key = f"predict_{json.dumps(features)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            app.logger.info(f'Serving cached prediction for features: {features}')
            return jsonify(cached_result)
        
        # Make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0].tolist()
        
        # Prepare response
        result = {
            "success": True,
            "prediction": int(prediction),
            "probability": probability,
            "features": features
        }
        
        # Cache the result
        cache.set(cache_key, result)
        
        app.logger.info(f'Prediction made for features: {features}, result: {prediction}')
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f'Error during prediction: {str(e)}')
        return jsonify({"success": False, "error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    app.logger.error(f'404 error: {error}')
    return jsonify({"success": False, "error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.error(f'500 error: {error}')
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1983) # Changed port to 1983 (my birth year!)