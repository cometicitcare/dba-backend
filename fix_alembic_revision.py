#!/usr/bin/env python3
"""
Fix alembic revision in the database
"""
import psycopg2
from urllib.parse import unquote

# Hardcoded connection string (parsed from alembic.ini)
conn_string = "host=gondola.proxy.rlwy.net port=22000 dbname=dbahrms-new user=app_admin password=rX2SWDbFuM%Qe3kBRzqnQ&Ia"

# Connect
conn = psycopg2.connect(conn_string)
cur = conn.cursor()

# Check current revision
cur.execute("SELECT version_num FROM alembic_version;")
current = cur.fetchone()
print(f"Current revision: {current[0]}")

# Update to match local chain
cur.execute("UPDATE alembic_version SET version_num='20251214000002' WHERE version_num='20251222000001';")
conn.commit()

# Verify
cur.execute("SELECT version_num FROM alembic_version;")
updated = cur.fetchone()
print(f"Updated revision: {updated[0]}")

cur.close()
conn.close()

print("✅ Alembic revision fixed!")
