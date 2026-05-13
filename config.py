# config.py
# Stores application configuration settings.
# We keep this separate so database credentials are not hard-coded in the main application.

import os

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management and security (change this to something random)
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # POSTGRESQL CONNECTION (use this if you have PostgreSQL)
    # Format: postgresql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2942003@localhost:5432/inventory_db'
    
    # Disable tracking modifications to save memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    