import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool

# conn_data = {
#     'dbname': str(os.environ('DB_NAME')),
#     'user': str(os.environ('DB_USER')),
#     'password': str(os.environ('DB_PASS')),
#     'host': str(os.environ('DB_IP')),
#     'port': str(os.environ('DB_PORT')),
# }
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

conn_data_local = {
    'dbname': str(os.getenv('DB_NAME')),
    'user': str(os.getenv('DB_USER')),
    'password': str(os.getenv('DB_PASS')),
    'host': str(os.getenv('DB_IP')),
    'port': str(os.getenv('DB_PORT')),
    'connect_timeout': 5,
} 

pool = AsyncConnectionPool(
    kwargs=conn_data_local,
    min_size=1,
    max_size=10,
    open=False,    
)
