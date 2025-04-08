import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sari_sari_store"
    )

# Function to get product stock information
def get_products():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT name, stock FROM products")
    products = cursor.fetchall()
    db.close()
    return products

# Function to get daily sales data (accurate)
def get_daily_sales_data():
    db = get_db_connection()
    cursor = db.cursor()
    query = """
        SELECT DATE(date) AS sale_date, SUM(price * quantity) AS total_sales
        FROM sales
        GROUP BY DATE(date)
        ORDER BY sale_date ASC
    """
    cursor.execute(query)
    daily_sales = cursor.fetchall()
    db.close()
    return daily_sales

# Function to get monthly sales data (accurate)
def get_monthly_sales_data():
    db = get_db_connection()
    cursor = db.cursor()
    query = """
        SELECT DATE_FORMAT(date, '%Y-%m') AS sale_month, SUM(price * quantity) AS total_sales
        FROM sales
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY sale_month ASC
    """
    cursor.execute(query)
    monthly_sales = cursor.fetchall()
    db.close()
    return monthly_sales
