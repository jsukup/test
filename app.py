from flask import Flask, jsonify
import logging

# Initialize Flask app
app = Flask(__name__)

# Set the logger level for Flask's logger
app.logger.setLevel(logging.INFO)

@app.route('/')
def hello():
    app.logger.info('Main endpoint processing HTTP request')
    return jsonify({"success":True, "message": "Hello, World!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=50505)