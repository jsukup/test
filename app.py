from flask import Flask, jsonify, request
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Initialize Flask app
app = Flask(__name__)

# Set the logger level for Flask's logger (BONUE FEATURE!)
app.logger.setLevel(logging.INFO)

# Create a simple ML model for demo purposes
def create_demo_model():
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 0])  # XOR function
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Save model if it doesn't exist
    if not os.path.exists('model.joblib'):
        joblib.dump(model, 'model.joblib')
    
    return model

# Load or create the model
model = create_demo_model()

@app.route('/')
def hello():
    app.logger.info('Main endpoint processing HTTP request')
    return jsonify({"success": True, "message": "Hello, Asling Partners! This is John, your new Applied AI Consultant."})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    app.logger.info('Health check endpoint called')
    return jsonify({"status": "healthy"})

@app.route('/api/v1/predict', methods=['POST'])
def predict():
    """Endpoint for ML model inference"""
    app.logger.info('Predict endpoint processing HTTP request')
    
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
        
        # Make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0].tolist()
        
        # Return prediction
        return jsonify({
            "success": True,
            "prediction": int(prediction),
            "probability": probability,
            "features": features
        })
    
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