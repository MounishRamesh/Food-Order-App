from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Database Connection
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='ramesh@05"',  # Remove the quote if not part of your actual password
        database='foods'
    )

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/place_order', methods=['POST'])
def place_order():
    connection = None
    cursor = None
    try:
        order_data = request.get_json()
        cart = order_data.get('cart')
        address = order_data.get('address')
        payment = order_data.get('payment')
        customer = order_data.get('customer')  # 👈 new

        if not cart or not address:
            return jsonify({"error": "Cart is empty or address missing"}), 400
        if not payment:
            return jsonify({"error": "Payment details missing"}), 400
        if not customer:
            return jsonify({"error": "Customer details missing"}), 400

        first_name = customer.get('first_name')
        last_name = customer.get('last_name')
        phone_number = customer.get('phone_number')
        email = customer.get('email')

        payment_method = payment.get('method')
        payment_status = payment.get('status')
        amount = payment.get('amount')

        connection = create_connection()
        cursor = connection.cursor()

        # Insert customer
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, phone_number, email)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, phone_number, email))
        customer_id = cursor.lastrowid

        # Insert orders
        order_ids = []
        for item in cart:
            item_name = item['name']
            quantity = item['quantity']

            cursor.execute("SELECT item_id FROM items WHERE item_name = %s", (item_name,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": f"Item {item_name} not found"}), 400

            item_id = result[0]

            cursor.execute("""
                INSERT INTO orders (user_id, item_id, quantity, delivery_address)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, item_id, quantity, address))
            order_ids.append(cursor.lastrowid)

        # Insert payment for the last order
        latest_order_id = order_ids[-1]
        cursor.execute("""
            INSERT INTO payments (order_id, payment_method, payment_status, amount)
            VALUES (%s, %s, %s, %s)
        """, (latest_order_id, payment_method, payment_status, amount))

        connection.commit()
        return jsonify({"message": "Customer, Order, and Payment placed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Fetch all Orders
@app.route('/orders', methods=['GET'])
def get_orders():
    connection = None
    cursor = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.order_id, o.delivery_address, p.payment_method, p.payment_status, p.amount
            FROM orders o
            JOIN payments p ON o.order_id = p.order_id
        """)
        orders = cursor.fetchall()
        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Add Customer
@app.route('/add_customer', methods=['POST'])
def add_customer():
    connection = None
    cursor = None
    try:
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        email = data.get('email')

        if not (first_name and last_name and phone_number and email):
            return jsonify({"error": "All fields are required"}), 400

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, phone_number, email)
            VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, phone_number, email))
        connection.commit()

        return jsonify({"message": "Customer added successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Get All Customers
@app.route('/customers', methods=['GET'])
def get_customers():
    connection = None
    cursor = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        return jsonify({"customers": customers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
