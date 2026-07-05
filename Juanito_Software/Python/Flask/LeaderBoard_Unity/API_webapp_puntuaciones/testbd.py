import psycopg2

try:
    connection = psycopg2.connect(
        dbname="Game",
        user="admin",
        password="admin",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Conectado a PostgreSQL, versión: {version[0]}")
except Exception as error:
    print(f"Error al conectar a PostgreSQL: {error}")
finally:
    if 'connection' in locals() and connection is not None:
        cursor.close()
        connection.close()
