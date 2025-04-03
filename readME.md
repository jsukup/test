# Flask Docker Skeleton Project

## Overview

This skeleton project provides a foundation for building a RESTful API using Flask and containerizing it with Docker. It's designed to test your skills in web development, API design, machine learning integration, and containerization.

## Tech Stack

- Python 3.11
- Flask: A lightweight WSGI web application framework
- Gunicorn: A Python WSGI HTTP Server for UNIX
- Docker: A platform for developing, shipping, and running applications

## Prerequisites

- Docker installed on your local machine

## Project Structure

'''
project_root/
├── Dockerfile
├── requirements.txt
├── app.py
└── README.md
'''

## Your Task

1. Implement the API in `app.py`, including an inference endpoint for a machine learning model
2. Build and run the Docker container
3. Make successful requests to your API

## Detailed Requirements

- Create an inference endpoint that accepts input data and returns predictions using a machine learning model of your choice
- Implement proper error handling and input validation
- Ensure the API follows RESTful principles

## Getting Started

### 1. API Implementation

- Open `app.py` and implement the required endpoints and logic
- Ensure your code follows PEP 8 style guidelines
- Add any necessary dependencies to `requirements.txt`

### 2. Building the Docker Image

```bash
docker build -t <image-name>:<version> .
```

### 3. Running the Container

```bash
docker run -p 50505:50505 <image-name>:<version>
```

### 4. Testing Your API

Use curl or any API testing tool to make requests to your endpoints. For example:

```bash  
curl http://localhost:50505
```

## Evaluation Criteria

Your submission will be evaluated based on:

- Correctness of API implementation, including the ML inference endpoint
- Code quality, organization, and adherence to best practices
- Proper use of Docker
- API functionality and adherence to RESTful principles
- Error handling and input validation

## Bonus Features

While not required, implementing any of the following will be viewed favorably:

- JWT authentication
- Comprehensive logging
- API documentation (e.g., using Swagger/OpenAPI)
- Unit tests
- Data validation and sanitization
- Rate limiting
- Caching mechanisms

## Submission and Review Process

1. When ready, we will schedule a meeting with you to review your implementation.

2. During this meeting, you will have the opportunity to walk us through your code live. Be prepared to:
   - Explain your design decisions
   - Demonstrate the functionality of your API
   - Discuss any challenges you faced and how you overcame them
   - Answer questions about your implementation

3. This live review allows us to better understand your thought process and gives you a chance to showcase your communication skills and technical knowledge.

We look forward to seeing your implementation and discussing it with you!

____

## IMPLEMENTATION DOCUMENTATION

### API Implementation

The following endpoints have been implemented:

1. `GET /` - Main endpoint that returns a simple hello message
2. `GET /health` - Health check endpoint to verify the API is running
3. `POST /api/v1/predict` - ML inference endpoint that accepts feature data and returns predictions

The ML inference endpoint uses a simple Random Forest Classifier trained on the XOR function as a demonstration. It accepts JSON input with a "features" key containing a list of 2 numeric values.

### Error Handling

Comprehensive error handling has been implemented:

- 400 Bad Request errors for invalid input data
- 404 Not Found errors for undefined routes
- 500 Internal Server errors for server-side exceptions
- Detailed error messages in the response body

### Dependencies

The following dependencies have been added:

- scikit-learn: For the Random Forest machine learning model
- numpy: For numerical operations
- joblib: For model serialization

### Building and Running the Container

1. Build the Docker image:

```bash
docker build -t flask-ml-api:1.0 .
```

2. Run the container:

```bash
docker run -p 1983:1983 flask-ml-api:1.0
```

### Testing the API

1. Test the main endpoint:

```bash
curl http://localhost:1983/
```

2. Test the health check:

```bash
curl http://localhost:1983/health
```

3. To get a JWT token for authentication:

```bash
curl -X POST http://localhost:1983/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

4. Extract and save the token to an environment variable:

```bash
# Extract the token from the response and save to TOKEN variable
export TOKEN="YOUR_TOKEN_HERE"  # Replace with your actual token
```

5. Test the ML inference endpoint:

```bash
curl -X POST http://localhost:1983/api/v1/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"features": [0, 1]}'
```

Expected response:

```json
{
  "features": [0, 1],
  "prediction": 1,
  "probability": [0.0, 1.0],
  "success": true
}
```

### Bonus Features Implemented

1. **JWT Authentication**
   - Added JWT-based authentication using Flask-JWT-Extended
   - Created a login endpoint at `/api/auth/login` 
   - Protected the prediction endpoint with JWT authentication
   - Tokens expire after 1 hour

2. **Comprehensive Logging**
   - Enhanced logging with proper formatting
   - Added detailed log messages for all operations
   - Included user identification in logs
   - Added error logging with stack traces

3. **API Documentation**
   - Added Swagger documentation using Flasgger
   - API docs available at `/docs/` endpoint
   - Complete documentation for all endpoints with examples
   - Authentication information included

4. **Unit Tests**
   - Added comprehensive test suite using pytest
   - Tests for all endpoints and error scenarios
   - Authentication testing
   - Input validation testing
   - Tests run automatically during Docker build

5. **Data Validation and Sanitization**
   - Added thorough validation for all input data
   - Type checking and length validation for feature inputs
   - JSON format validation for requests
   - Proper error responses for invalid inputs

6. **Rate Limiting**
   - Implemented rate limiting with Flask-Limiter
   - Differentiated limits for various endpoints:
     - Main endpoint: 10 requests per minute
     - Health check: 60 requests per minute
     - Login: 10 requests per minute 
     - Prediction: 30 requests per minute
   - Global limits of 200 requests per day and 50 per hour

7. **Caching Mechanisms**
   - Added response caching with Flask-Caching
   - Home endpoint cached for 60 seconds
   - Health check cached for 10 seconds
   - Prediction results cached based on input features
   - Cache utilizes memory storage with 5-minute default timeout

### Swagger Documentation

```bash
# Open in browser
http://localhost:1983/docs/
```