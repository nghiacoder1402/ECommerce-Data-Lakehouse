import pyodbc


SERVER = "localhost"
DATABASE = "ECommerceDB"
DRIVER = "ODBC Driver 18 for SQL Server"


def get_connection():
    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


if __name__ == "__main__":
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME()")

    database_name = cursor.fetchone()[0]

    print(f"Connected to database: {database_name}")

    cursor.close()
    conn.close()