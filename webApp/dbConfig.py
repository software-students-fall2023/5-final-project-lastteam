# db_config.py
import os

DB_URI = os.getenv('DB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'pokerPro')
