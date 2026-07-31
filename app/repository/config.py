import os

PG_HOST = os.environ.get('PG_HOST', '')
PG_PORT = os.environ.get('PG_PORT', '5432')
PG_DATABASE = os.environ.get('PG_DATABASE', '')
PG_SCHEMA = os.environ.get('PG_SCHEMA', '')
PG_USER = os.environ.get("PG_USER", '')
PG_PASSWORD = os.environ.get("PG_PASSWORD", '')


POSTGRES_CONFIG = {
    "host": PG_HOST,
    "port": int(PG_PORT),
    "database": PG_DATABASE,
    "user": PG_USER,
    "password": PG_PASSWORD,
    "sslmode": "prefer",
    "gssencmode": "disable"
}
