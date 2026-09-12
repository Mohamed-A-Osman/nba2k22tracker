"""AWS Lambda entry point: runs the Flask app behind API Gateway."""
from apig_wsgi import make_lambda_handler

from app import app

handler = make_lambda_handler(app, binary_support=True)
