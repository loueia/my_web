from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
from database import get_products, get_daily_sales_data, get_monthly_sales_data

app = Flask(__name__)
app.secret_key = "secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sari_sari_store"
)
cursor = db.cursor(dictionary=True)

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect('/home')
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

# Home Page
@app.route('/home')
def home():
    products = get_products()
    daily_sales_data = get_daily_sales_data()    # List of tuples: (sale_date, total_sales)
    monthly_sales_data = get_monthly_sales_data()  # List of tuples: (sale_month, total_sales)

    # Process daily sales data
    daily_dates = [str(row[0]) for row in daily_sales_data]
    daily_values = [row[1] for row in daily_sales_data]

    # Process monthly sales data
    monthly_dates = [str(row[0]) for row in monthly_sales_data]
    monthly_values = [row[1] for row in monthly_sales_data]

    return render_template('home.html', 
                           products=products, 
                           daily_dates=daily_dates, 
                           daily_values=daily_values,
                           monthly_dates=monthly_dates, 
                           monthly_values=monthly_values)

# View All Products
@app.route('/products')
def products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('products.html', products=products)

# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        data = (
            request.form['product_number'],
            request.form['name'],
            request.form['price'],
            request.form['stock']
        )
        cursor.execute("INSERT INTO products (product_number, name, price, stock) VALUES (%s, %s, %s, %s)", data)
        db.commit()
        flash('Product added successfully!')
        return redirect('/products')
    return render_template('add_product.html')

# Update and Delete Product
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()
    if request.method == 'POST':
        data = (
            request.form['product_number'],
            request.form['name'],
            request.form['price'],
            request.form['stock'],
            id
        )
        cursor.execute("UPDATE products SET product_number=%s, name=%s, price=%s, stock=%s WHERE id=%s", data)
        db.commit()
        flash('Product updated!')
        return redirect('/products')
    return render_template('add_product.html', product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    # Delete sales records for this product first
    cursor.execute("DELETE FROM sales WHERE product_id = %s", (id,))
    # Then delete the product
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    db.commit()
    flash('Product and its associated sales have been deleted!')
    return redirect('/products')

# Search Product
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        cursor.execute("SELECT * FROM products WHERE product_number LIKE %s OR name LIKE %s", 
                       (f"%{keyword}%", f"%{keyword}%"))
        results = cursor.fetchall()
        return render_template('products.html', products=results)
    return redirect('/products')

# Purchase Page
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])

        cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cursor.fetchone()

        if product and product['stock'] >= quantity:
            total_price = product['price'] * quantity
            cursor.execute("INSERT INTO purchases (product_id, quantity, total_price) VALUES (%s, %s, %s)",
                           (product_id, quantity, total_price))
            cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (quantity, product_id))
            db.commit()
            flash('Purchase successful!')
            return render_template('receipt.html', product=product, quantity=quantity, total=total_price)
        else:
            flash('Not enough stock!')
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('purchase.html', products=products)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
